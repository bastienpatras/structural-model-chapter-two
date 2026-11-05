"""
enrich_listings.py
==================
Enriches a listings parquet (from collect_listings.py) with ADEME DPE certificates.

For each listing, attempts to find a matching ADEME DPE record using address_id,
area, floor, and publication date.  Adds three columns to the parquet:
  - K                : 1 if a certified ADEME DPE was found, 0 otherwise
  - ademe_epc_letter : matched DPE letter (A–G), NaN when K=0
  - ademe_epc_score  : numeric 1–7 (A=1 … G=7), NaN when K=0

The address_id in the listings (geo.geo_address2.id) is converted to the
legacy geo ID (geo.geo_identifiers.place_id) before matching, so it sits in
the same ID space as the ADEME DPE geocoded data on GCS.

Usage:
    python enrich_listings.py \\
        --input  data/listings_APARTMENT.parquet \\
        --output data/listings_enriched_APARTMENT.parquet \\
        [--departments 75,13,69] \\
        [--save-to-gcs] \\
        [--min-score 0.3]
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg2
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from match_improved import match
from tools import gcs_file_exists, read_csv_from_gcs


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            f"enrich_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
    ],
)
logger = logging.getLogger(__name__)

_EPC_LETTER_TO_SCORE = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}

# GCS constants — overridable via environment
GCS_BUCKET        = os.environ.get("GCS_BUCKET", "ma-data-dev")
ADEME_DPE_PREFIX  = os.environ.get("GCS_ADEME_DPE_PREFIX", "ADEME/DPE/ADEME_GEOCODED_SUBREGION_CODE_")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db_connection():
    host     = os.environ.get("DB_HOST", "localhost")
    port     = os.environ.get("DB_PORT", "4444")
    user     = os.environ.get("DB_USER", "ma_data")
    password = os.environ.get("DB_PASSWORD", "")
    dbname   = os.environ.get("DB_NAME", "listing_dev")
    uri      = f"postgresql://{user}@{host}:{port}/{dbname}"
    return psycopg2.connect(uri, password=password)


def add_legacy_geo_for_listings(listings_df: pd.DataFrame, conn) -> pd.DataFrame:
    """
    Set id_legacy for listings.

    geo.geo_identifiers maps:  id (HONUFR… external)  →  place_id (= geo.geo_address2.id)
    So the DPE side converts id_aviv → place_id via that table.
    The listing's address_id IS already geo.geo_address2.id, i.e. it IS the place_id.
    No DB lookup is needed — we just expose it under the id_legacy name.
    """
    listings_df = listings_df.copy()
    listings_df["id_legacy"] = pd.to_numeric(listings_df["address_id"], errors="coerce")
    n_valid = listings_df["id_legacy"].notna().sum()
    logger.info(f"   id_legacy set directly from address_id: {n_valid:,} valid")
    return listings_df


# ---------------------------------------------------------------------------
# DPE data loader (identical to run_listings.py)
# ---------------------------------------------------------------------------

def load_dpe_data(department_code: str, conn) -> pd.DataFrame | None:
    """Load geocoded ADEME DPE data from GCS for one department."""
    bucket_name = GCS_BUCKET
    file_name = f"{ADEME_DPE_PREFIX}{department_code}"

    if not gcs_file_exists(bucket_name, file_name):
        logger.warning(f"   DPE data not found for department {department_code}")
        return None

    df = read_csv_from_gcs(bucket_name, file_name)

    if "area" not in df.columns and "surface_habitable_logement" in df.columns:
        df["area"] = df["surface_habitable_logement"].apply(
            lambda x: round(x, 2) if pd.notna(x) else x
        )

    # Convert ADEME id_aviv → id_legacy (same as run_listings.py)
    df = _add_legacy_geo_for_dpe(df, conn)
    return df


def _add_legacy_geo_for_dpe(dpe_df: pd.DataFrame, conn) -> pd.DataFrame:
    """
    Convert DPE id_aviv to id_legacy (= geo.geo_address2.id = listing address_id).

    geo.geo_identifiers maps:  id (HONUFR… external)  →  place_id (= geo.geo_address2.id)
    We look up each unique id_aviv in that table to get the canonical place_id,
    which sits in the same ID space as the listing's address_id.
    """
    dpe_df = dpe_df.copy()

    unique_ids = dpe_df["id_aviv"].dropna().unique().tolist()
    if not unique_ids:
        dpe_df["id_legacy"] = np.nan
        return dpe_df

    # Batch lookup in geo.geo_identifiers (chunked to avoid huge IN clauses)
    CHUNK = 10_000
    rows = []
    cur = conn.cursor()
    for i in range(0, len(unique_ids), CHUNK):
        chunk = unique_ids[i : i + CHUNK]
        placeholders = ",".join(["%s"] * len(chunk))
        cur.execute(
            f"SELECT id, place_id FROM geo.geo_identifiers WHERE id IN ({placeholders})",
            chunk,
        )
        rows.extend(cur.fetchall())
    cur.close()

    lookup = pd.DataFrame(rows, columns=["id_aviv", "place_id"])
    lookup["place_id"] = pd.to_numeric(lookup["place_id"], errors="coerce")

    dpe_df = dpe_df.merge(lookup, on="id_aviv", how="left")
    dpe_df["id_legacy"] = dpe_df["place_id"]
    dpe_df = dpe_df.drop(columns=["place_id"])

    n_valid = dpe_df["id_legacy"].notna().sum()
    n_total = len(dpe_df)
    logger.info(
        f"   DPE id_legacy from geo.geo_identifiers: {n_valid:,}/{n_total:,} "
        f"({n_valid/n_total:.1%}) records have a valid address mapping"
    )
    return dpe_df


# ---------------------------------------------------------------------------
# Main enrichment function
# ---------------------------------------------------------------------------

def enrich_listings(
    listings_path: str | Path,
    output_path: str | Path,
    conn,
    departments: list | None = None,
    save_to_gcs: bool = False,
    min_score: float = 0.3,
    directory: str = "listings",
) -> pd.DataFrame:
    """
    Enrich listings with ADEME DPE data and save the result.

    Parameters
    ----------
    listings_path : path to parquet produced by collect_listings.py
    output_path   : where to save the enriched parquet
    conn          : open psycopg2 connection to listing_dev
    departments   : list of department COG codes to process; default = all in data
    save_to_gcs   : if True, match() exports intermediate results to GCS
    min_score     : minimum match_score to accept a DPE match (default 0.3)
    directory     : GCS subdirectory used by match() for exports

    Returns
    -------
    pd.DataFrame  : enriched listings (also saved to output_path)
    """
    df = pd.read_parquet(listings_path)
    logger.info(f"Loaded {len(df):,} listings from {listings_path}")

    required = {"address_id", "cog", "item_type", "start_date", "size_m2", "floor_num"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Listings parquet is missing columns needed for ADEME matching: {missing}. "
            "Re-run collect_listings.py — these columns are added automatically."
        )

    # ── Step 1: batch geo lookup for all listings ────────────────────────────
    df = add_legacy_geo_for_listings(df, conn)
    no_legacy = df["id_legacy"].isna().sum()
    if no_legacy:
        logger.warning(
            f"   {no_legacy:,} listings have no id_legacy mapping — they will get K=0"
        )

    # ── Step 2: derive department code from COG (first 2 chars) ─────────────
    def _cog_to_dept(cog: str) -> str:
        cog = str(cog).zfill(5)
        prefix = cog[:2]
        return cog[:3] if prefix == "97" else prefix

    df["dept"] = df["cog"].dropna().astype(str).map(_cog_to_dept)

    if departments is None:
        departments = sorted(df["dept"].dropna().unique().tolist())
    logger.info(f"Departments to process: {len(departments)}")

    # ── Step 3: per-department matching ─────────────────────────────────────
    enrichment_parts = []
    total_start = time.time()

    for i, dept in enumerate(departments, 1):
        dept_str = dept if dept in ("2A", "2B") else str(dept).zfill(2)
        logger.info(f"\n[{i}/{len(departments)}] Department {dept_str}")

        dept_listings = df[df["dept"] == dept_str].copy()
        if len(dept_listings) == 0:
            logger.info("   No listings — skipping")
            continue

        logger.info(f"   Listings: {len(dept_listings):,}")

        # Load DPE data
        dpe_df = load_dpe_data(dept_str, conn)
        if dpe_df is None or len(dpe_df) == 0:
            logger.warning(f"   No DPE data — K=0 for all {len(dept_listings):,} listings")
            enrichment_parts.append(
                pd.DataFrame({
                    "listing_id": dept_listings["listing_id"],
                    "K": 0,
                    "ademe_epc_letter": np.nan,
                    "ademe_epc_score": np.nan,
                    "match_score": np.nan,
                })
            )
            continue

        logger.info(f"   DPE records: {len(dpe_df):,}")

        # Rename to match() expected schema:
        #   id, address_id, street_id, floor, area, sale_agreement_date,
        #   energy_consumption_classification, item_type
        match_df = dept_listings.drop(columns=["floor"], errors="ignore").rename(columns={
            "listing_id": "id",
            "size_m2": "area",
            "start_date": "sale_agreement_date",
            "floor_num": "floor",   # use raw numeric floor for matching
        }).copy()

        # Use id_legacy as the address key (same ID space as DPE data)
        match_df["address_id"] = match_df["id_legacy"]

        # Disclosed EPC letter for validation comparison inside match()
        score_to_letter = {v: k for k, v in _EPC_LETTER_TO_SCORE.items()}
        match_df["energy_consumption_classification"] = match_df.apply(
            lambda r: score_to_letter.get(int(r["epc_score"]))
            if r["d"] == 1 and pd.notna(r.get("epc_score"))
            else None,
            axis=1,
        )

        try:
            master, _, _, _ = match(
                df=match_df,
                searcher_df=dpe_df,
                saved=save_to_gcs,
                min_score_threshold=min_score,
                directory=directory,
            )
        except Exception as e:
            logger.error(f"   Matching failed: {e}")
            continue

        # Build K lookup from match results
        lookup = (
            master[["sale_id", "ademe_dpe", "match_score"]]
            .rename(columns={"sale_id": "listing_id"})
            .copy()
        )
        lookup["K"] = lookup["ademe_dpe"].notna().astype(int)
        lookup["ademe_epc_letter"] = lookup["ademe_dpe"]
        lookup["ademe_epc_score"] = lookup["ademe_dpe"].map(_EPC_LETTER_TO_SCORE)

        enrichment_parts.append(
            lookup[["listing_id", "K", "ademe_epc_letter", "ademe_epc_score", "match_score"]]
        )

        matched = lookup["K"].sum()
        logger.info(
            f"   Matched: {matched:,}/{len(dept_listings):,} "
            f"({matched/len(dept_listings):.1%})"
        )

    # ── Step 4: merge enrichment back ────────────────────────────────────────
    if enrichment_parts:
        enrichment = pd.concat(enrichment_parts, ignore_index=True)
        df = df.merge(enrichment, on="listing_id", how="left")
    else:
        df["K"] = np.nan
        df["ademe_epc_letter"] = np.nan
        df["ademe_epc_score"] = np.nan
        df["match_score"] = np.nan

    # Listings from departments with no DPE data get K=0
    df["K"] = df["K"].fillna(0).astype(int)

    # ── Step 5: drop matching helper columns ─────────────────────────────────
    df = df.drop(
        columns=["address_id", "street_id", "id_legacy", "cog", "item_type"],
        errors="ignore",
    )

    # ── Step 6: save ─────────────────────────────────────────────────────────
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    elapsed = (time.time() - total_start) / 60
    logger.info(f"Enrichment complete in {elapsed:.1f} min — saved → {output_path}")
    log_enrichment_report(df)

    return df


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def compute_match_statistics(df: pd.DataFrame) -> dict:
    """
    Compute overall statistics from the enriched listings DataFrame.

    Covers three dimensions:
    - Match quality  : K rate, match_score distribution
    - Group breakdown: (K, d) classification that maps to the structural groups
                       in data_prep.classify_listings()
    - EPC accuracy   : for K=1 & d=1, compare self-reported epc_score
                       with ademe_epc_score (exact matches, advantageous /
                       disadvantageous reporting errors)

    Parameters
    ----------
    df : enriched listings DataFrame (output of enrich_listings())

    Returns
    -------
    dict with keys: match, groups, accuracy
    """
    n = len(df)

    # ── Match quality ────────────────────────────────────────────────────────
    k1 = int(df["K"].sum())
    scored = df["match_score"].dropna()
    match_stats = {
        "total_listings"   : n,
        "matched"          : k1,
        "match_rate"       : k1 / n if n else 0.0,
        "score_p25"        : float(scored.quantile(0.25)) if len(scored) else None,
        "score_median"     : float(scored.quantile(0.50)) if len(scored) else None,
        "score_p75"        : float(scored.quantile(0.75)) if len(scored) else None,
        "score_mean"       : float(scored.mean())         if len(scored) else None,
    }

    # ── Group breakdown (K × d) ──────────────────────────────────────────────
    # Maps directly to the groups in data_prep.classify_listings():
    #   K=1, d=1 → truthful disclosure
    #   K=1, d=0 → strategic hiding
    #   K=0, d=0 → uninformed
    #   K=0, d=1 → unverified disclosers (ADEME coverage gap or matching failure)
    grp = df.groupby(["K", "d"]).size()
    group_stats = {
        "truthful_disclosure"    : int(grp.get((1, 1), 0)),
        "strategic_hiding"       : int(grp.get((1, 0), 0)),
        "uninformed"             : int(grp.get((0, 0), 0)),
        "unverified_disclosers"  : int(grp.get((0, 1), 0)),
    }

    # ── EPC accuracy for K=1, d=1 ────────────────────────────────────────────
    # Advantageous error: seller discloses a *better* class than ADEME certified
    # (epc_score < ademe_epc_score, since A=1 is best and G=7 is worst).
    both = df[
        (df["K"] == 1) & (df["d"] == 1)
        & df["epc_score"].notna() & df["ademe_epc_score"].notna()
    ].copy()

    if len(both) == 0:
        accuracy_stats = {
            "validation_sample"       : 0,
            "exact_match_rate"        : None,
            "advantageous_error_rate" : None,
            "disadvantageous_error_rate": None,
        }
    else:
        diff        = (both["epc_score"] - both["ademe_epc_score"]).to_numpy()
        exact       = int(np.sum(diff == 0))
        adv_errors  = int(np.sum(diff  < 0))   # claims better class
        disadv_err  = int(np.sum(diff  > 0))   # claims worse class
        m = len(both)
        accuracy_stats = {
            "validation_sample"         : m,
            "exact_match_rate"          : exact / m,
            "advantageous_error_rate"   : adv_errors / m,
            "disadvantageous_error_rate": disadv_err / m,
        }

    return {"match": match_stats, "groups": group_stats, "accuracy": accuracy_stats}


def compute_department_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-department breakdown of match rate, K rate, and group counts.

    Parameters
    ----------
    df : enriched listings DataFrame (must have a 'cog' column; note that
         'cog' is dropped from the final parquet — pass the DataFrame before
         that step, or re-attach cog from the original parquet if needed)

    Returns
    -------
    pd.DataFrame indexed by department COG with columns:
        total, matched, match_rate, K_rate,
        truthful_disclosure, strategic_hiding, uninformed, unverified_disclosers
    """
    if "cog" not in df.columns:
        raise ValueError(
            "'cog' column not found. Pass the DataFrame before helper columns "
            "are dropped, or merge COG back from the original listings parquet."
        )

    rows = []
    for dept, grp in df.groupby("cog"):
        n   = len(grp)
        k1  = int(grp["K"].sum())
        kd  = grp.groupby(["K", "d"]).size()
        rows.append({
            "cog"                    : dept,
            "total"                  : n,
            "matched"                : k1,
            "match_rate"             : k1 / n if n else 0.0,
            "truthful_disclosure"    : int(kd.get((1, 1), 0)),
            "strategic_hiding"       : int(kd.get((1, 0), 0)),
            "uninformed"             : int(kd.get((0, 0), 0)),
            "unverified_disclosers"  : int(kd.get((0, 1), 0)),
        })

    return pd.DataFrame(rows).set_index("cog").sort_index()


def log_enrichment_report(df: pd.DataFrame) -> dict:
    """
    Compute statistics and write a formatted summary to the logger.

    Called automatically at the end of enrich_listings().
    Can also be called manually on any enriched parquet:

        df = pd.read_parquet("data/listings_enriched_APARTMENT.parquet")
        stats = log_enrichment_report(df)

    Returns
    -------
    dict from compute_match_statistics()
    """
    stats = compute_match_statistics(df)
    m  = stats["match"]
    g  = stats["groups"]
    a  = stats["accuracy"]

    logger.info(f"\n{'='*60}")
    logger.info("ENRICHMENT REPORT")
    logger.info(f"{'='*60}")

    logger.info(f"\n── Match quality ({'─'*38})")
    logger.info(f"  Total listings : {m['total_listings']:>10,}")
    logger.info(f"  Matched (K=1)  : {m['matched']:>10,}  ({m['match_rate']:.1%})")
    if m["score_median"] is not None:
        logger.info(
            f"  Match score    :  p25={m['score_p25']:.3f}  "
            f"median={m['score_median']:.3f}  p75={m['score_p75']:.3f}  "
            f"mean={m['score_mean']:.3f}"
        )

    logger.info(f"\n── Group breakdown ({'─'*35})")
    total = m["total_listings"] or 1
    logger.info(f"  Truthful disclosure     : {g['truthful_disclosure']:>8,}  ({g['truthful_disclosure']/total:.1%})")
    logger.info(f"  Strategic hiding        : {g['strategic_hiding']:>8,}  ({g['strategic_hiding']/total:.1%})")
    logger.info(f"  Uninformed              : {g['uninformed']:>8,}  ({g['uninformed']/total:.1%})")
    logger.info(f"  Unverified disclosers   : {g['unverified_disclosers']:>8,}  ({g['unverified_disclosers']/total:.1%})")

    logger.info(f"\n── EPC accuracy  (K=1 & d=1) ({'─'*24})")
    if a["validation_sample"] == 0:
        logger.info("  No validation sample available")
    else:
        logger.info(f"  Validation sample       : {a['validation_sample']:>8,}")
        logger.info(f"  Exact match rate        : {a['exact_match_rate']:>8.1%}")
        logger.info(f"  Advantageous errors     : {a['advantageous_error_rate']:>8.1%}  (discloses better than ADEME)")
        logger.info(f"  Disadvantageous errors  : {a['disadvantageous_error_rate']:>8.1%}  (discloses worse than ADEME)")

    logger.info(f"{'='*60}\n")
    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Enrich listings parquet with ADEME DPE data (adds K, ademe_epc_score)"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/listings_APARTMENT.parquet",
        help="Path to listings parquet from collect_listings.py",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/listings_enriched_APARTMENT.parquet",
        help="Output path for enriched parquet",
    )
    parser.add_argument(
        "--departments",
        type=str,
        default=None,
        help="Comma-separated department codes (e.g. '75,13,69'). Default: all in data.",
    )
    parser.add_argument(
        "--save-to-gcs",
        action="store_true",
        help="Export per-department match results to GCS (same layout as run_listings.py)",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.3,
        help="Minimum match_score to accept a DPE match (default 0.3)",
    )

    args = parser.parse_args()

    departments = (
        [d.strip() for d in args.departments.split(",")]
        if args.departments
        else None
    )

    # Auto-tag output path with item_type read from the input parquet
    # (e.g. data/listings_enriched_APARTMENT.parquet → data/listings_enriched_APARTMENT.parquet).
    # Reads only the first row to extract the item_type column cheaply.
    import pandas as _pd
    from pathlib import Path as _Path
    try:
        _item_type = _pd.read_parquet(args.input, columns=["item_type"]).iloc[0]["item_type"]
        _p = _Path(args.output)
        if _item_type.upper() not in _p.stem.upper():
            args.output = str(_p.parent / f"{_p.stem}_{_item_type.upper()}{_p.suffix}")
        logger.info(f"Item type detected: {_item_type} → output: {args.output}")
    except Exception:
        pass  # if item_type column missing or file unreadable, keep output as-is

    logger.info("Connecting to database...")
    conn = get_db_connection()

    try:
        enrich_listings(
            listings_path=args.input,
            output_path=args.output,
            conn=conn,
            departments=departments,
            save_to_gcs=args.save_to_gcs,
            min_score=args.min_score,
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()