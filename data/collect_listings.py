from __future__ import annotations

import os
import pickle
from io import BytesIO
import numpy as np
import pandas as pd
import psycopg2
import geopandas as gpd
from dotenv import find_dotenv, load_dotenv
from google.cloud import storage
from shapely import wkt
from pathlib import Path

load_dotenv(find_dotenv())


def get_db_uri() -> str:
    """Build a psycopg2-compatible URI from environment variables."""
    host     = os.environ.get("DB_HOST", "localhost")
    port     = os.environ.get("DB_PORT", "4444")
    user     = os.environ.get("DB_USER", "ma_data")
    password = os.environ.get("DB_PASSWORD", "")
    dbname   = os.environ.get("DB_NAME", "listing_dev")
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


# ---------------------------------------------------------------------------
# EPC letter → numeric score (used by data_prep.binarise_epc)
# ---------------------------------------------------------------------------

_EPC_LETTER_TO_SCORE = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7}


def epc_letter_to_score(letter: str) -> float:
    """Map EPC letter A–G to integer 1–7. Returns NaN for anything else."""
    return float(_EPC_LETTER_TO_SCORE.get(str(letter).upper().strip(), np.nan))


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def create_dates(date_to: str, month_count: int) -> pd.DatetimeIndex:
    """Monthly date range from (date_to − month_count months) to date_to."""
    date_end   = pd.Timestamp(date_to)
    date_start = date_end - pd.DateOffset(months=month_count)
    return pd.date_range(date_start, date_end, freq='MS')

def read_pickle(file_name: str, bucket_name: str="ma-data-dev"):
    # Initialize GCS client
    client = storage.Client(project="ma-data-dev")
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Download the pickle file into memory
    pickle_data = blob.download_as_bytes()

    # Load the pickle data
    with BytesIO(pickle_data) as file:
        return pickle.load(file)


# ---------------------------------------------------------------------------
# DB query
# ---------------------------------------------------------------------------

def get_obs(
        geo_id: tuple,
        geo_label: str,
        date_to: str,
        item_type: str,
        transaction_type: str,
        month_count: int,
        uri: str
):
    # Calculate and format dates
    date_from_str = f"'{(pd.Timestamp(date_to) - pd.DateOffset(months=month_count)).strftime('%Y-%m-%d')}'"
    date_to_str = f"'{date_to}'"

    # SQL Request
    sql = f"""

        SELECT

            listing.external_id AS listing_id,

            COALESCE(address.city_id, listing.city_id) AS city_id,
            address.block_id,
            address.neighborhood_id,
            place.region_id,
            place.subregion_id,
            address.borough_id,
            address.iris_id,
            street.id AS street_id,
            place.cog AS cog,

            listing.price::FLOAT,
            listing.energy_certificate_efficiency_score AS energy_consumption,
            listing.energy_certificate_overall_energy_need AS consoenergie,
            listing.energy_certificate_yearly_greenhouse_gaz_emission AS emissionges,
            listing.energy_source_electric,
            listing.item_type,
            listing.is_offerer_individual AS client_type,

            CAST(listing.publish_start_date AS DATE) AS start_date,
            CAST(listing.publish_end_date AS DATE) AS end_date,
            listing.is_offerer_individual::INTEGER AS client_type,
            listing.parking_garage_count::INTEGER AS parking_count,
            listing.has_passenger_lift::INTEGER AS elevator,
            listing.bathroom_count::INTEGER AS bathrooms,
            listing.client_id::INTEGER AS realtor_ref,
            listing.build_year::INTEGER AS built_year,
            listing.has_cellar::INTEGER  AS cellar,
            listing.room_count::INTEGER AS rooms,
            listing.address_id::INTEGER ,
            listing.floor::INTEGER,
            listing.area::FLOAT

        FROM listing_seloger.aggregate AS listing

        LEFT JOIN geo.geo_address2 address ON (
                listing.address_id = address.id
                AND address.enabled = True
                )

        LEFT JOIN geo.geo_street2 street ON (
                listing.street_id = street.id
                AND street.enabled = True
                )

        LEFT JOIN geo.geo_block2 block ON (
                listing.block_id = block.id
                AND block.enabled = True
                )

        LEFT JOIN geo.geo_place2 place ON (
                listing.city_id = place.id
                AND place.enabled = True
                AND type = 40
                )

        WHERE listing.transaction_type = 'TRANSACTION_TYPE.{transaction_type}'
            AND listing.area::FLOAT BETWEEN 9 AND 250
            AND (listing.item_type = 'ITEM_TYPE.{item_type}')
            AND listing.{geo_label} in {geo_id}
            AND CAST(listing.publish_start_date as DATE) >= {date_from_str}
            AND CAST(listing.publish_start_date as DATE) < {date_to_str}
            AND listing.client_id<> 453

        """
    return pd.read_sql(sql, uri)


# ---------------------------------------------------------------------------
# Preprocessing helpers
# ---------------------------------------------------------------------------

def preprocess_df(df: pd.DataFrame, max_price_m2_thousands: float) -> pd.DataFrame:
    """
    Compute price_m2 and apply basic price sanity filters.

    Parameters
    ----------
    df                    : raw listings from get_obs()
    max_price_m2_thousands: upper price/m² cap in thousands of EUR
                            (250 → 250,000 EUR/m² for apartments; 300 for houses)
    """
    df = df.dropna(subset=['price', 'area']).copy()
    df['price']    = df['price'].astype(float)
    df['area']     = df['area'].astype(float)
    df['price_m2'] = df['price'] / df['area']
    df = df[df['price_m2'].between(500, max_price_m2_thousands * 1000)]
    return df.reset_index(drop=True)


def apply_dynamic_filters(df: pd.DataFrame, dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Retain listings whose start_date falls within the given monthly date range."""
    df = df.copy()
    df['start_date'] = pd.to_datetime(df['start_date'])
    mask = (df['start_date'] >= dates.min()) & (df['start_date'] <= dates.max())
    return df[mask].reset_index(drop=True)


def get_observations_filtered_sell(

        geo_id: tuple,
        geo_label: str,
        date_to: str,
        item_type: str,
        transaction_type: str,
        month_count: int,
        uri: str

):
    # Get observations
    observations = get_obs(
        geo_id,
        geo_label,
        date_to,
        item_type,
        transaction_type,
        month_count,
        uri,
    )
    # Create date filtering
    dates = create_dates(date_to, month_count)

    if item_type == 'APARTMENT':
        df_apa = preprocess_df(observations.copy(), 250)
        df_apa = apply_dynamic_filters(df_apa, dates)
        return df_apa

    elif item_type == 'HOUSE':
        df_ma = preprocess_df(observations.copy(), 15)
        df_ma = df_ma.loc[
            (df_ma['price'].between(20000, 2000000)) &
            ((df_ma['area'] / df_ma['rooms']).between(8, 50))
            ]
        df_ma = apply_dynamic_filters(df_ma, dates)
        return df_ma


# ---------------------------------------------------------------------------
# Column-level processing (hedonic regression controls)
# ---------------------------------------------------------------------------

def process_energy_consumption(data, by_cat):
    data['EPC'] = np.select(
        [
            data.energy_consumption == 'ENERGY.CERTIFICATE_EFFICIENCY_SCORE.A',
            data.energy_consumption == 'ENERGY.CERTIFICATE_EFFICIENCY_SCORE.B',
            data.energy_consumption == 'ENERGY.CERTIFICATE_EFFICIENCY_SCORE.C',
            data.energy_consumption == 'ENERGY.CERTIFICATE_EFFICIENCY_SCORE.D',
            data.energy_consumption == 'ENERGY.CERTIFICATE_EFFICIENCY_SCORE.E',
            data.energy_consumption == 'ENERGY.CERTIFICATE_EFFICIENCY_SCORE.F',
            data.energy_consumption == 'ENERGY.CERTIFICATE_EFFICIENCY_SCORE.G',
        ],
        [
            'A', 'B', 'C', 'D', 'E', 'F', 'G'
        ],
        default='Missing'
    )

    if by_cat is True:
        data['energy_consumption'] = np.select(
            [
                data.EPC.isin(['A', 'B', 'C']),
                data.EPC.isin(['D', 'E']),
                data.EPC.isin(['F', 'G']),
            ],
            ['ABC', 'DE', 'FG'],
            default='Missing'
        )

    return data


def process_built_year(data):
    data['built_year'] = data.built_year.apply(
        lambda x: '1799' if x < 1800 else
        ('1800_1914' if x < 1915 else
         ('1915_1945' if x < 1946 else
          ('1946_1974' if x < 1975 else
           ('1975_1990' if x < 1991 else
            ('1991_2003' if x < 2004 else
             ('2004' if x >= 2004 else 'built_year_NA'))))))
    )
    return data


def process_floor(data):
    data['floor'] = data['floor'].apply(
        lambda x: "floor_7up" if x >= 7 else ("eNA" if x < 0 else x)
    )
    data['floor'] = data['floor'].fillna("floor_NA")
    data['floor'] = data['floor'].apply(lambda x: "floor_0" if x == 0 else x)
    data['floor'] = data['floor'].apply(lambda x: "floor_123" if x in [1, 2, 3] else x)
    data['floor'] = data['floor'].apply(lambda x: "floor_456" if x in [4, 5, 6] else x)
    return data


def process_elevator(data):
    data['elevator'] = data['elevator'].fillna(False)
    data['elevator'] = data['elevator'].astype(int)
    return data


def process_rooms(data):
    data['rooms'] = data['rooms'].apply(lambda x: f"room_count_5up" if x >= 5 else x)
    data['rooms'] = data['rooms'].apply(lambda x: f"room_count_{x}" if x in range(5) else x)
    data['rooms'] = data['rooms'].fillna("room_count_NA")
    return data


def process_cellar(data):
    data['cellar'] = data['cellar'].fillna(0).astype(int)
    return data


def process_bathrooms(data):
    data['bathrooms'] = data['bathrooms'].apply(
        lambda x: "bathrooms_NA" if pd.isna(x) else f"bathrooms_{int(x)}"
    )
    return data


def process_log_price(data):
    data['sqm_price_log'] = np.log(data['price_m2'].astype(float))
    return data


def process_log_area(data):
    data['area_log'] = np.log(data['area'].astype(float) / 50)
    return data


def get_semester(date):
    month = date.month
    if month in [1, 2, 3, 4, 5, 6]:
        return f'{date.year}S1'
    else:
        return f'{date.year}S2'


def process_date_controls(data, nb_month):
    data['start_date'] = pd.to_datetime(data['start_date'])

    if nb_month == 3:
        data['time'] = [i.strftime('%YQ%q') for i in data['start_date'].dt.to_period('Q')]
    elif nb_month == 1:
        data['time'] = data['start_date'].apply(lambda x: x.replace(day=1))
    elif nb_month == 3 * 2:
        data['time'] = data['start_date'].apply(get_semester)
    else:
        data['time'] = [str(i.year) + 'Y' for i in pd.to_datetime(data['start_date'])]

    return data

def get_geopandas(df: pd.DataFrame, geom_col: str = "geom", crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    wdata = df.copy()
    if 'cluster_id' in wdata.columns:
        wdata = wdata.drop_duplicates(subset=[geom_col, 'city_id', 'cluster_id'])
    else:
        wdata = wdata.drop_duplicates(subset=[geom_col, 'city_id'])

    # Convert only valid WKT strings to geometry; skip NaN or invalid types
    def safe_load_wkt(x):
        if isinstance(x, str) and x.strip():  # must be a non-empty string
            try:
                return wkt.loads(x)
            except Exception:
                return None
        return None

    wdata["geometry"] = wdata[geom_col].apply(safe_load_wkt)

    # Drop rows without geometry (optional, but recommended)
    wdata = wdata.dropna(subset=["geometry"])

    # Return a GeoDataFrame
    return gpd.GeoDataFrame(wdata, geometry="geometry", crs=crs)

def get_cluster_mapped(df: pd.DataFrame) -> gpd.GeoDataFrame:
    # Copy the input data to avoid mutating it
    wdata = df.copy()
    wdata = get_geopandas(wdata.dropna(subset=["geom"]), crs="EPSG:4326")

    # Extract ID and type from cluster key
    wdata["cluster_key"] = wdata["cluster_id"].astype(str)
    wdata["cluster_id"] = wdata["cluster_key"].apply(lambda x: x[2:len(x)]).astype(str)

    # Group geometries by cluster_id
    clustered = (
        wdata
        .dissolve(by="cluster_id", as_index=False)  # merges geometries
        .reset_index(drop=True)
    )

    return clustered[["cluster_id", "cluster_key", "CATEAAV2020_LABEL", "geometry",  "distance"]]

def get_clusters(
    data: pd.DataFrame,
    clusters_path: str = os.environ.get("GCS_CLUSTERS_PATH", "These/Bastien/DIFFINDISC/geo-culsters.plk"),
) -> pd.DataFrame:
    """
    Merge urban-area cluster attributes (CATEAAV2020_LABEL, distance) into listings.

    Loads the raw cluster pickle (one row per municipality/cog), then left-joins
    on the `cog` column.  get_cluster_mapped() is intentionally not called here
    because it dissolves by cluster_id, which drops the cog key needed for merging.
    """
    geo_raw = read_pickle(clusters_path)
    geo_raw.columns = [c.lower() for c in geo_raw.columns]

    # Keep only the columns needed; drop duplicates so the merge is 1-to-1 on cog
    keep = ['cog'] + [c for c in ['cateaav2020_label', 'distance', 'cluster_id', 'cluster_key']
                      if c in geo_raw.columns]
    geo_raw = geo_raw[keep].drop_duplicates(subset=['cog'])

    # Split cluster_id into prefix (cateaav2020 code) and city-centre COG (market_id).
    # Format: {N-char prefix}{5-char COG} — take last 5 chars so the split is robust
    # to any prefix length rather than assuming a fixed 2-char offset.
    raw = geo_raw["cluster_id"].astype(str)
    geo_raw["cluster_key"] = raw                          # preserve original
    geo_raw["cluster_id"]  = raw.str[-5:]                 # city-centre COG → market_id

    return pd.merge(data, geo_raw, on='cog', how='left')


def process_cluster_controls(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean cluster variables for use as hedonic regression controls.

    - cateaav2020_label : fill missing with 'unknown' so it is never NaN in OLS
    - distance          : winsorise at the 99th percentile to limit outlier leverage
    """
    if 'cateaav2020_label' in data.columns:
        data['cateaav2020_label'] = data['cateaav2020_label'].fillna('unknown')

    if 'distance' in data.columns:
        cap = data['distance'].quantile(0.99)
        data['distance'] = data['distance'].clip(upper=cap)

    return data


def process_data(
        data: pd.DataFrame,
        by_cat: bool,
        nb_month: int,
        clusters_path: str | None = None,
):
    data = process_energy_consumption(data, by_cat)
    data = process_built_year(data)
    # Preserve raw numeric floor for ADEME matching before binning
    data['floor_num'] = pd.to_numeric(data['floor'], errors='coerce')
    data = process_floor(data)
    data = process_elevator(data)
    data = process_rooms(data)
    data = process_cellar(data)
    data = process_log_price(data)
    data = process_log_area(data)
    data = process_date_controls(data, nb_month)
    data = process_bathrooms(data)
    if clusters_path is not None:
        data = get_clusters(data, clusters_path)
        data = process_cluster_controls(data)
    return data


# ---------------------------------------------------------------------------
# Bridge: transform to data_prep.py schema
# ---------------------------------------------------------------------------

def prepare_listings_for_estimation(
    df_raw: pd.DataFrame,
    market_geo_col: str = 'cluster_id',
    by_cat: bool = False,
    nb_month: int = 3,
    clusters_path: str | None = None,
) -> pd.DataFrame:
    """
    Transform raw SeLoger listings (from get_observations_filtered_sell) into
    the schema expected by data_prep.py.

    Parameters
    ----------
    df_raw         : output of get_observations_filtered_sell() — unprocessed
    market_geo_col : geo column to use as market_id.
                     Options: 'cluster_id', 'iris_id', 'city_id', 'neighborhood_id', 'borough_id'
    by_cat         : passed to process_data() for EPC grouping
    nb_month       : passed to process_data() for time-period granularity
    clusters_path  : GCS path to the urban-area cluster pickle (e.g.
                     "These/Bastien/DIFFINDISC/geo-culsters.plk").
                     When provided, cateaav2020_label and distance are merged in
                     and included in the output for use as hedonic controls.

    Returns
    -------
    pd.DataFrame with columns:
      listing_id, market_id, log_price, d, epc_score, size_m2, built_year,
      rooms, floor, elevator, cellar, bathrooms,
      [cateaav2020_label, distance]  — when clusters_path is provided

    Schema notes
    ------------
    - log_price         : log(price / area) — log price per m²
    - d                 : 1 if EPC letter displayed (A–G), 0 if 'Missing'
    - epc_score         : numeric 1–7 (A=1 … G=7); NaN when d=0
    - market_id         : df_raw[market_geo_col] (rows with null market_id dropped)
    - size_m2           : listing area in m²
    - built_year        : construction period category (e.g. '1946_1974') produced
                          by process_built_year(); auto-dummified by statsmodels
    - cateaav2020_label : urban-area classification (categorical, hedonic control)
    - distance          : distance to urban centre in km (continuous, hedonic control)
    """
    df = df_raw.copy()

    # ── hedonic preprocessing + optional cluster enrichment ──────────────────
    # built_year is categorised into period bins by process_built_year() inside
    # process_data(); keep raw integer until then so the column is not lost.
    df = process_data(df, by_cat=by_cat, nb_month=nb_month, clusters_path=clusters_path)

    # ── market_id ─────────────────────────────────────────────────────────────
    if market_geo_col not in df.columns:
        available = [c for c in df.columns if any(k in c for k in ('id', 'cog'))]
        raise ValueError(
            f"market_geo_col='{market_geo_col}' not found in DataFrame. "
            f"Available geo-like columns: {available}"
        )
    df = df.rename(columns={market_geo_col: 'market_id'})
    df = df.dropna(subset=['market_id'])

    # ── log_price (log price per m²) ─────────────────────────────────────────
    df['log_price'] = df['sqm_price_log']   # already computed by process_log_price

    # ── d: EPC disclosed? ────────────────────────────────────────────────────
    df['d'] = df['EPC'].isin(['A', 'B', 'C', 'D', 'E', 'F', 'G']).astype(int)

    # ── epc_score: numeric 1–7 for binarise_epc ─────────────────────────────
    df['epc_score'] = df['EPC'].apply(
        lambda x: epc_letter_to_score(x) if x != 'Missing' else np.nan
    )

    # ── size_m2 ───────────────────────────────────────────────────────────────
    df = df.rename(columns={'area': 'size_m2'})

    # ── item_type: clean to APARTMENT / HOUSE for ADEME matching ─────────────
    if 'item_type' in df.columns:
        df['item_type'] = (
            df['item_type']
            .map({'ITEM_TYPE.APARTMENT': 'APARTMENT', 'ITEM_TYPE.HOUSE': 'HOUSE'})
            .fillna(df['item_type'])
        )

    # ── Drop rows missing mandatory ADEME matching fields ────────────────────
    # address_id and size_m2 are required for all item types.
    # floor_num is only mandatory for APARTMENT: houses don't have a floor number
    # and ADEME matching falls back to area+address matching when floor is absent.
    _is_apartment = (
        df["item_type"].iloc[0].upper() == "APARTMENT"
        if "item_type" in df.columns and len(df) > 0
        else True
    )
    _mandatory_cols = ['address_id', 'size_m2'] + (['floor_num'] if _is_apartment else [])
    mandatory = [c for c in _mandatory_cols if c in df.columns]
    before = len(df)
    df = df.dropna(subset=mandatory)
    dropped = before - len(df)
    if dropped:
        print(f"Dropped {dropped:,} rows missing mandatory matching fields "
              f"({dropped / before:.1%} of {before:,})")

    # ── Select output columns ────────────────────────────────────────────────
    base    = ['listing_id', 'market_id', 'log_price', 'd', 'epc_score', 'EPC', 'size_m2', 'built_year']
    geo     = [c for c in ['region_id', 'subregion_id', 'city_id', 'neighborhood_id', 'borough_id']
               if c in df.columns]
    hedonic = [c for c in ['rooms', 'floor', 'elevator', 'cellar', 'bathrooms', 'parking_count']
               if c in df.columns]
    cluster = [c for c in ['cateaav2020_label', 'distance', 'cluster_id', 'geometry']
               if c in df.columns]
    # Kept for ADEME enrichment step (enrich_listings.py); dropped after K is added.
    matching = [c for c in ['address_id', 'street_id', 'cog', 'item_type', 'start_date', 'floor_num']
                if c in df.columns]
    return df[base + geo + hedonic + cluster + matching].reset_index(drop=True)


# ---------------------------------------------------------------------------
# End-to-end pipeline: collect from DB → transform → save
# ---------------------------------------------------------------------------

def collect_and_save_listings(
    geo_id: tuple,
    geo_label: str,
    date_to: str,
    item_type: str,
    month_count: int,
    uri: str,
    save_path: str | Path = 'data/listings_APARTMENT.parquet',
    market_geo_col: str = 'iris_id',
    by_cat: bool = False,
    nb_month: int = 3,
    clusters_path: str | None = None,
) -> pd.DataFrame:
    """
    Full pipeline: DB → preprocess → data_prep schema → save as Parquet.

    The saved file is read by main.py via data_prep.load_listings().

    Parameters
    ----------
    geo_id, geo_label : geographic filter (e.g., tuple of IRIS ids, 'iris_id')
    date_to           : collection window end date ('YYYY-MM-DD')
    item_type         : 'APARTMENT' or 'HOUSE'
    month_count       : lookback window in months
    uri               : database connection URI (psycopg2 format)
    save_path         : output Parquet path (default: 'data/listings_APARTMENT.parquet')
    market_geo_col    : geo column used as market_id in data_prep
    by_cat            : if True, group EPC into ABC/DE/FG
    nb_month          : time-period granularity for hedonic dummies
    clusters_path     : GCS path to the urban-area cluster pickle; when provided,
                        cateaav2020_label and distance are added as hedonic controls

    Returns
    -------
    pd.DataFrame in data_prep.py format (also saved to save_path)
    """
    df_raw = get_observations_filtered_sell(
        geo_id=geo_id,
        geo_label=geo_label,
        date_to=date_to,
        item_type=item_type,
        transaction_type='SELL',
        month_count=month_count,
        uri=uri,
    )

    df_out = prepare_listings_for_estimation(
        df_raw,
        market_geo_col=market_geo_col,
        by_cat=by_cat,
        nb_month=nb_month,
        clusters_path=clusters_path,
    )

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_parquet(save_path, index=False)
    print(f"Saved {len(df_out):,} listings → {save_path}")

    return df_out


# ---------------------------------------------------------------------------
# CLI entry point — reads all parameters from .env
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    geo_ids_raw = os.environ.get("LISTINGS_GEO_IDS", "").strip().strip("[]")
    if not geo_ids_raw:
        raise SystemExit("Error: LISTINGS_GEO_IDS is not set in .env")

    geo_id    = tuple(int(x.strip()) for x in geo_ids_raw.split(",") if x.strip())
    geo_label = os.environ.get("LISTINGS_GEO_LABEL", "subregion_id")
    date_to   = os.environ.get("LISTINGS_DATE_TO", "2024-12-01")
    item_type = os.environ.get("LISTINGS_ITEM_TYPE", "APARTMENT")
    month_count = int(os.environ.get("LISTINGS_MONTH_COUNT", "12"))
    nb_month    = int(os.environ.get("LISTINGS_NB_MONTH", "3"))
    by_cat      = os.environ.get("LISTINGS_BY_CAT", "0") == "1"
    save_path   = os.environ.get("LISTINGS_SAVE_PATH", "data/listings_APARTMENT.parquet")
    market_geo_col = os.environ.get("LISTINGS_MARKET_GEO_COL", "subregion_id")
    clusters_path  = os.environ.get("GCS_CLUSTERS_PATH") or None

    # Auto-tag save_path with item_type (e.g. data/listings_APARTMENT.parquet →
    # data/listings_APARTMENT.parquet) so apartment and house files don't overwrite each other.
    _p = Path(save_path)
    if item_type.upper() not in _p.stem.upper():
        save_path = str(_p.parent / f"{_p.stem}_{item_type.upper()}{_p.suffix}")

    uri = get_db_uri()

    print(f"Collecting {item_type} listings  |  geo_label={geo_label}  |  {len(geo_id)} IDs")
    print(f"Window: {month_count} months up to {date_to}  |  save → {save_path}")

    collect_and_save_listings(
        geo_id=geo_id,
        geo_label=geo_label,
        date_to=date_to,
        item_type=item_type,
        month_count=month_count,
        uri=uri,
        save_path=save_path,
        market_geo_col=market_geo_col,
        by_cat=by_cat,
        nb_month=nb_month,
        clusters_path=clusters_path,
    )
