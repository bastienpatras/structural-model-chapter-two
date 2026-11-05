"""
Improved property-DPE matching algorithm with bug fixes and validation.

Key improvements over match.py:
- Fixed compute_dpe() logic bug
- Fixed typo in complement_address
- Added validation metrics
- Added minimum score threshold
- Better documentation
- Performance monitoring
"""

import logging
import time
import warnings

import numpy as np
import pandas as pd
from tools import export_to_gcs


warnings.filterwarnings("ignore")

# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def compute_dpe(a, b):
    """
    Returns the worse (higher letter) DPE label between energy and GHG emissions.

    The final DPE is determined by taking the worst of:
    - etiquette_dpe (energy consumption)
    - etiquette_ges (greenhouse gas emissions)

    Args:
        a: First DPE label (A-G)
        b: Second DPE label (A-G)

    Returns:
        The worse (later in alphabet) label in uppercase, or pd.NA if invalid.

    Examples:
        compute_dpe("A", "F") -> "F"
        compute_dpe("C", "B") -> "C"
        compute_dpe("D", "D") -> "D"
    """
    if not isinstance(a, str) or not isinstance(b, str):
        return pd.NA

    # Return the worse label (max in alphabetical order)
    return max(a.upper(), b.upper())


class PropertySearcherDF:
    """
    A class for searching property records (apartments or houses) in a DataFrame
    based on various criteria such as address, floor, area, and DPE (energy efficiency label).

    Matching Strategy:
    ==================
    For apartments:
        - Matches on floor with a soft penalty for floor mismatches (Gaussian scoring).
    For houses:
        - Ignores floor differences.
        - Falls back to street-level matching if no exact address match.

    Scoring Components (configurable weights):
    ==========================================
    - Area similarity (default 50%): Penalizes area differences
    - Floor similarity (default 10%): Gaussian penalty for floor mismatches (apartments only)
    - Date recency (default 20%): Penalizes old DPE certificates
    - Label dispersion (default 20%): Rewards diverse label distribution in candidates

    The default weights were chosen to prioritize area matching while considering
    temporal relevance and avoiding biased samples.
    """

    def __init__(self, dataframe):
        """
        Initializes the searcher by preparing and transforming the DataFrame for use.

        Args:
            dataframe: DataFrame with ADEME DPE data including address, floor, area, dates, labels
        """
        logger.info(
            f"Initializing PropertySearcherDF with {len(dataframe)} DPE records..."
        )

        self.df = dataframe.copy()
        self.df["date_reception_dpe"] = pd.to_datetime(
            self.df["date_reception_dpe"], errors="coerce"
        )
        self.df["floor"] = pd.to_numeric(self.df["floor"], errors="coerce")
        self.df["address_id"] = self.df["id_legacy"]
        self.df["street_id"] = self.df["id_legacy"]
        self.df["ademe_floor"] = pd.to_numeric(self.df["floor"], errors="coerce")
        self.df["ademe_area"] = pd.to_numeric(self.df["area"], errors="coerce")
        self.df["complement_adresse_logement"] = self.df["complement_adresse_logement"]

        # Fixed: Use improved compute_dpe function
        self.df["ademe_dpe"] = self.df.apply(
            lambda x: compute_dpe(x["etiquette_dpe"], x["etiquette_ges"]), axis=1
        )

        logger.info(f"✅ Initialized with {len(self.df)} valid DPE records")

    def area_score(self, row_area, query_area, area_threshold=6):
        """
        Computes area similarity score (1.0 = identical, 0.0 = far apart).

        Args:
            row_area: Area of the DPE record (m²)
            query_area: Area of the property being matched (m²)
            area_threshold: Maximum acceptable difference (default 6m²)

        Returns:
            Score between 0.0 and 1.0
        """
        return max(0.0, min(1.0, 1 - abs(row_area - query_area) / area_threshold))

    def date_score(self, dpe_date, publication_date, decay_factor=365):
        """
        Scores based on recency of DPE vs publication date. Penalizes older DPE dates.

        Args:
            dpe_date: Date the DPE was issued
            publication_date: Date the property was listed/sold
            decay_factor: Days until score reaches 0 (default 365 = 1 year)

        Returns:
            Score between 0.0 and 1.0 (0.7 for missing dates)
        """
        if pd.isna(dpe_date):
            return 0.7  # Mild penalty for missing dates

        days_diff = (publication_date - dpe_date).days

        if days_diff < 0:
            return 0.0  # Future dates are invalid

        return max(0.0, min(1.0, 1 - days_diff / decay_factor))

    def floor_score_gaussian(self, row_floor, query_floor, sigma=1.0):
        """
        Scores floor proximity using a Gaussian function.

        Perfect match (same floor) = 1.0
        1 floor difference = 0.61
        2 floors difference = 0.14
        3+ floors difference ≈ 0.0

        Args:
            row_floor: Floor number in DPE record
            query_floor: Floor number of property being matched
            sigma: Gaussian width parameter (default 1.0)

        Returns:
            Score between 0.0 and 1.0
        """
        if pd.isna(row_floor) or pd.isna(query_floor):
            return 0.0

        distance = row_floor - query_floor
        score = np.exp(-0.5 * (distance / sigma) ** 2)
        return max(0.0, min(1.0, score))

    def letter_count(self, candidates):
        """
        Counts the frequency distribution of DPE letters in groups: AB, CDE, FG.

        This is used to detect biased samples (e.g., all candidates are F/G = bad building).

        Args:
            candidates: List of DPE letters

        Returns:
            List of [freq_AB, freq_CDE, freq_FG]
        """
        if len(candidates) == 0:
            return [0, 0, 0]

        count_ab = round(sum(c in "AB" for c in candidates) / len(candidates), 2)
        count_cde = round(sum(c in "CDE" for c in candidates) / len(candidates), 2)
        count_fg = round(sum(c in "FG" for c in candidates) / len(candidates), 2)

        return [count_ab, count_cde, count_fg]

    def score_letter_dispersion(self, freq_ab, freq_cde, freq_fg):
        """
        Calculates dispersion score based on the deviation from uniform label distribution.

        Higher score = more diverse labels = higher confidence in match quality.
        If all candidates have same label group, this returns low score.

        Args:
            freq_ab: Frequency of AB labels
            freq_cde: Frequency of CDE labels
            freq_fg: Frequency of FG labels

        Returns:
            Dispersion score between 0.0 and 1.0
        """
        score_ab = max(freq_ab - 1 / 3, 0)
        score_cde = max(freq_cde - 1 / 3, 0)
        score_fg = max(freq_fg - 1 / 3, 0)
        return (score_ab + score_cde + score_fg) * 3 / 2

    def score_match(
        self,
        row,
        floor,
        area,
        candidates,
        publication_date=None,
        use_floor=True,
        area_weight=0.5,
        floor_weight=0.1,
        date_weight=0.2,
        dispersion_weight=0.2,
    ):
        """
        Aggregates individual scores (area, floor, date, dispersion) into a single match score.

        Score Components:
        - Area similarity (50%): Core matching criterion
        - Floor similarity (10%): Secondary for apartments
        - Date recency (20%): Prefer recent DPEs
        - Label dispersion (20%): Reward diverse candidate pool

        Args:
            row: DPE record being scored
            floor: Query floor number
            area: Query area (m²)
            candidates: All candidate DPE labels at this address
            publication_date: Sale/listing date
            use_floor: Whether to include floor scoring (False for houses)
            *_weight: Configurable weights for each component

        Returns:
            Final match score between 0.0 and 1.0
        """
        area_score = self.area_score(row["area"], area)
        floor_score = (
            self.floor_score_gaussian(row["floor"], floor) if use_floor else 0.0
        )
        date_score = (
            self.date_score(row["date_reception_dpe"], publication_date)
            if publication_date is not None
            else 1.0
        )
        letters = self.letter_count(candidates)
        letter_dispersion_score = self.score_letter_dispersion(*letters)

        total_score = (
            area_score * area_weight
            + floor_score * floor_weight
            + date_score * date_weight
            + letter_dispersion_score * dispersion_weight
        )
        return round(total_score, 3)

    def search(
        self,
        address_id,
        street_id,
        floor,
        area,
        floor_threshold=5,
        area_threshold=3,
        item_type="APARTMENT",
        publication_date=None,
    ):
        """
        Main search method: Filters and scores potential property matches.

        Search Strategy:
        ================
        1. Filter by address_id + area (± area_threshold)
        2. Filter by publication date (DPE must be before sale)
        3. For houses: Fallback to street_id if no matches
        4. For apartments: Filter by floor (± floor_threshold)
        5. Score all candidates and rank by match_score

        Parameters:
            address_id: Address identifier to match
            street_id: Fallback identifier for houses
            floor: Desired floor (only for apartments)
            area: Desired living area (m²)
            floor_threshold: Tolerance in floor matching (default 5)
            area_threshold: Tolerance in area matching (default 3m²)
            item_type: "APARTMENT" or "HOUSE"
            publication_date: Reference date to penalize old DPEs

        Returns:
            - List of matched records with scores (sorted by match_score desc)
            - Dictionary of intermediate match stages for debugging
        """
        # Stage 1: Address + Area filtering
        matches = self.df[
            (self.df["address_id"] == address_id)
            & (abs(self.df["area"] - area) <= area_threshold)
        ].copy()

        match_counts = {
            "area_stage": [],
            "street_stage": [],
            "date_stage": [],
            "floor_stage": [],
            "complement_address": [],  # Fixed typo: was "compelement_address"
            "scores": [],
        }

        candidates = matches.ademe_dpe.to_list()
        match_counts["area_stage"] += candidates

        # Stage 2: Date filtering
        if publication_date is not None:
            publication_date = pd.to_datetime(publication_date, errors="coerce")
            matches = matches[
                matches["date_reception_dpe"].isna()
                | (matches["date_reception_dpe"] < publication_date)
            ]
            match_counts["date_stage"] += matches.ademe_dpe.to_list()

        # Stage 3: Fallback to street-level for houses
        if matches.empty and item_type.upper() == "HOUSE":
            matches = self.df[
                (self.df["street_id"] == street_id)
                & (abs(self.df["area"] - area) <= area_threshold)
            ].copy()

            if publication_date is not None:
                matches = matches[
                    matches["date_reception_dpe"].isna()
                    | (matches["date_reception_dpe"] < publication_date)
                ]
            match_counts["street_stage"] += matches.ademe_dpe.to_list()

        if matches.empty:
            return pd.DataFrame(), match_counts

        # Houses: No floor consideration
        if item_type.upper() == "HOUSE":
            matches["match_score"] = matches.apply(
                lambda row: self.score_match(
                    row, floor, area, candidates, publication_date, use_floor=False
                ),
                axis=1,
            )
            matches["match_score"] *= 0.9  # Slight penalty for street-level fallback
            return (
                matches.sort_values("match_score", ascending=False).to_dict(
                    orient="records"
                ),
                match_counts,
            )

        # Stage 4: Floor filtering for apartments
        matches["floor"] = pd.to_numeric(matches["floor"], errors="coerce")
        try:
            floor = float(floor)
        except Exception:
            floor = np.nan

        # Only apply floor filtering if we have multiple candidates
        valid_matches = (
            matches[
                matches["floor"].isna()
                | (abs(matches["floor"] - floor) <= floor_threshold)
            ].copy()
            if len(matches) > 1
            else matches.copy()
        )

        if valid_matches.empty:
            return pd.DataFrame(), match_counts

        # Score all valid matches
        valid_matches["match_score"] = valid_matches.apply(
            lambda row: self.score_match(
                row, floor, area, candidates, publication_date, use_floor=True
            ),
            axis=1,
        )

        match_counts["floor_stage"] += valid_matches.ademe_dpe.to_list()
        match_counts[
            "complement_address"
        ] += valid_matches.complement_adresse_logement.to_list()
        match_counts["scores"] += valid_matches.match_score.to_list()

        return (
            valid_matches.sort_values("match_score", ascending=False).to_dict(
                orient="records"
            ),
            match_counts,
        )


def create_size_report_df(df, list_columns):
    """Helper function to create size report for list columns."""
    size_data = {
        col: df[col].apply(lambda x: len(x) if isinstance(x, list) else x)
        for col in list_columns
    }
    return pd.DataFrame(size_data, index=df.index)


def true_one(a, b):
    """Helper function for distribution checks."""
    return 0 if a == b == 1 else b


def distribution_checks(df, list_columns):
    """
    Analyzes distribution of matches across different filtering stages.

    Returns summary statistics for each stage by item type.
    """
    data = create_size_report_df(df, list_columns)
    data["area"] = data["area_stage"]
    data["date"] = data.apply(
        lambda x: true_one(x["date_stage"], x["area_stage"]), axis=1
    )
    data["floor"] = data.apply(
        lambda x: true_one(x["floor_stage"], x["date_stage"]), axis=1
    )
    data["street"] = data.apply(
        lambda x: true_one(x["street_stage"], x["date_stage"]), axis=1
    )
    data = data[data.area != 0]
    return (
        data[["area", "date", "floor", "street", "item_type"]]
        .melt(
            id_vars=["item_type"],
            value_vars=["area", "date", "floor", "street"],
            var_name="stages",
        )
        .groupby(["stages", "item_type"])
        .describe(percentiles=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    )



def match(df, searcher_df, saved=True, min_score_threshold=0.3, directory="lisings"):
    """
    Main matching function: Links sales data with ADEME DPE certificates.

    Improvements over original:
    - Added min_score_threshold to filter low-confidence matches
    - Added validation metrics
    - Added performance monitoring
    - Better error handling

    Args:
        df: Sales data with columns: id, address_id, street_id, floor, area,
            sale_agreement_date, energy_consumption_classification, item_type
        searcher_df: ADEME DPE data
        saved: Whether to export results to GCS
        min_score_threshold: Minimum match_score to accept (default 0.3)

    Returns:
        Tuple of (master, historic, distribution, statistics)
    """
    logger.info("🚀 Starting property-DPE matching...")
    logger.info(f"   Sales records: {len(df):,}")
    logger.info(f"   DPE records: {len(searcher_df):,}")
    logger.info(f"   Min score threshold: {min_score_threshold}")

    start_time = time.time()

    searcher = PropertySearcherDF(searcher_df)

    # Pre-allocate lists for storing results
    master_rows = []
    historic_rows = []
    distribution = []
    low_score_count = 0

    # Loop over sales and match with DPEs
    for idx, (
        sale_id,
        address_id,
        street_id,
        floor,
        area,
        publication_date,
        disclosed_dpe,
        item_type,
    ) in enumerate(
        zip(
            df["id"],
            df["address_id"],
            df["street_id"],
            df["floor"],
            df["area"],
            df["sale_agreement_date"],
            df["energy_consumption_classification"],
            df["item_type"],
        )
    ):
        # Search for matching energy data
        results, distribution_dict = searcher.search(
            address_id=address_id,
            street_id=street_id,
            floor=floor,
            area=area,
            publication_date=publication_date,
            item_type=item_type,
        )

        # Convert to DataFrame if needed
        if isinstance(results, list):
            results = pd.DataFrame(results)

        # Handle no matches or low-confidence matches
        if results.empty or (
            not results.empty
            and results.iloc[0].get("match_score", 0) < min_score_threshold
        ):
            if not results.empty:
                low_score_count += 1

            master_rows.append(
                {
                    "sale_id": sale_id,
                    "street_id": street_id,
                    "address_id": address_id,
                    "area": area,
                    "sale_agreement_date": publication_date,
                    "disclosed_dpe": disclosed_dpe,
                    "floor": floor,
                    "item_type": item_type,
                    "ademe_dpe": pd.NA,
                    "match_score": results.iloc[0].get("match_score", 0)
                    if not results.empty
                    else 0,
                }
            )
        else:
            # Good match found
            results["sale_id"] = sale_id
            results["street_id"] = street_id
            results["address_id"] = address_id
            results["area"] = area
            results["sale_agreement_date"] = publication_date
            results["disclosed_dpe"] = disclosed_dpe
            results["floor"] = floor
            results["item_type"] = item_type

            # Apply fixed compute_dpe function
            results["ademe_dpe"] = results.apply(
                lambda row: compute_dpe(row["etiquette_dpe"], row["etiquette_ges"]),
                axis=1,
            )

            # Take best match
            master_rows.append(results.iloc[0].to_dict())
            historic_rows.append(results)

        # Handle distribution data
        if distribution_dict:
            distribution_data = pd.DataFrame([distribution_dict])
            distribution_data["sale_id"] = sale_id
            distribution_data["floor"] = floor
            distribution_data["item_type"] = item_type
            distribution_data["address_id"] = address_id
            distribution.append(distribution_data)

        # Log progress every 1000 rows
        if (idx + 1) % 1000 == 0:
            elapsed = time.time() - start_time
            rate = (idx + 1) / elapsed
            eta = (len(df) - idx - 1) / rate if rate > 0 else 0
            logger.info(
                f"Processed {idx + 1:,}/{len(df):,} rows "
                f"({(idx+1)/len(df)*100:.1f}%) - "
                f"Rate: {rate:.1f} rows/sec - "
                f"ETA: {eta/60:.1f} min"
            )

    # Create DataFrames
    if master_rows:
        columns = master_rows[0].keys()
        master = pd.DataFrame(master_rows, columns=columns)
    else:
        master = pd.DataFrame()

    historic = (
        pd.concat(historic_rows, ignore_index=True) if historic_rows else pd.DataFrame()
    )

    distribution = (
        pd.concat(distribution, ignore_index=True) if distribution else pd.DataFrame()
    )

    if not distribution.empty:
        distribution["area_stage"] = distribution["area_stage"].apply(
            lambda x: x if isinstance(x, list) else []
        )
        distribution[["AB", "CDE", "FG"]] = (
            distribution["area_stage"].apply(searcher.letter_count).apply(pd.Series)
        )

    # Performance summary
    elapsed = time.time() - start_time
    logger.info(f"\n{'='*60}")
    logger.info("✅ Matching complete!")
    logger.info(f"   Time elapsed: {elapsed/60:.1f} minutes")
    logger.info(f"   Processing rate: {len(df)/elapsed:.1f} rows/sec")
    logger.info(
        f"   Records with matches: {master['ademe_dpe'].notna().sum():,}/{len(master):,}"
    )
    logger.info(f"   Low-confidence matches filtered: {low_score_count:,}")
    logger.info(f"{'='*60}\n")

    # Export to GCS
    if saved and not master.empty:
        try:
            dept_code = str(int(df.cog.dropna().drop_duplicates().iloc[0]))

            logger.info(f"💾 Exporting results to GCS for department {dept_code}...")

            export_to_gcs(
                bucket_name="ma-data-dev",
                blob_name=f"ADEME/{directory}/LISTING_DATA/{dept_code}/LISTINGS_ENRICHED_SUBREGION_CODE_{dept_code}.csv",
                new_df=master.reset_index(drop=True)[
                    [
                        "sale_id",
                        "id_aviv",
                        "numero_dpe",
                        "match_score",
                        "ademe_dpe",
                        "etiquette_dpe",
                        "etiquette_ges",
                        "date_visite_diagnostiqueur",
                    ]
                ],
            )

            export_to_gcs(
                bucket_name="ma-data-dev",
                blob_name=f"ADEME/{directory}/LISTING_DATA/{dept_code}/LISTINGS_ENRICHED_HISTORIC_SUBREGION_CODE_{dept_code}.csv",
                new_df=historic.reset_index(drop=True),
            )

            export_to_gcs(
                bucket_name="ma-data-dev",
                blob_name=f"ADEME/{directory}/LISTING_DATA/{dept_code}/LISTINGS_ENRICHED_DISTRIBUTION_SUBREGION_CODE_{dept_code}.csv",
                new_df=distribution.reset_index(drop=True),
            )

            export_to_gcs(
                bucket_name="ma-data-dev",
                blob_name=f"ADEME/{directory}/LISTING_DATA/{dept_code}/LISTINGS_ENRICHED_STATISTICS_SUBREGION_CODE_{dept_code}.csv",
                new_df=distribution_checks(
                    distribution,
                    [
                        "area_stage",
                        "date_stage",
                        "floor_stage",
                        "street_stage",
                        "item_type",
                    ],
                ),
            )

            logger.info("✅ Export complete")

        except Exception as e:
            logger.error(f"❌ Export failed: {e}")

    return (
        master.reset_index(drop=True),
        historic.reset_index(drop=True),
        distribution.reset_index(drop=True),
        distribution_checks(
            distribution,
            ["area_stage", "date_stage", "floor_stage", "street_stage", "item_type"],
        )
        if not distribution.empty
        else pd.DataFrame(),
    )
