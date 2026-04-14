"""
Run DPE matching for all French departments and generate a summary report.

This script:
1. Iterates through all metropolitan French departments (01-95)
2. Loads DPE data from GCS for each department
3. Fetches sales data from the database
4. Runs the improved matching algorithm
5. Generates a per-department report with key metrics

Usage:
    python run_past_sales.py [--departments 75,13,69] [--date-min 2024-01-01]
"""

import argparse
import logging
import sys
import time
import warnings
from datetime import datetime

import pandas as pd
import psycopg2
from match_improved import compute_dpe, match
from tools import gcs_file_exists, read_csv_from_gcs


warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            f"matching_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
    ],
)
logger = logging.getLogger(__name__)


# Database configuration
DB_CONFIG = {
    "user": "meilleursagents",
    "password": "****",
    "database": "meilleursagents_prod",
    "host": "localhost",
    "port": 3333,
}


def get_db_connection():
    """Establish database connection."""
    uri = f"postgresql://{DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return psycopg2.connect(uri, password=DB_CONFIG["password"])


def add_legacy_geo(
    data: pd.DataFrame,
):
    # Connection to the database bv
    DEFAULT_DB_CONFIG = {
        "user": "meilleursagents",
        "password": "****",  # Replace with actual password
        "database": "meilleursagents_prod",
        "host": "localhost",  # You can change this to the host of your database if needed
        "port": 3333,
    }

    # Establish the connection using the config dictionary
    custom_uri = psycopg2.connect(
        user=DEFAULT_DB_CONFIG["user"],
        password=DEFAULT_DB_CONFIG["password"],
        database=DEFAULT_DB_CONFIG["database"],
        host=DEFAULT_DB_CONFIG["host"],
        port=DEFAULT_DB_CONFIG["port"],
    )

    # Ensure the ids are quoted properly (if they are strings)
    id_list = "','".join(
        map(str, data["id_aviv"].to_list())
    )  # Ensure to convert to string and quote

    # Prepare SQL query
    sql = f"""
    SELECT
        id AS id_aviv,
        place_id AS id_legacy,
        label AS geo_code
    FROM geo.geo_identifiers
    WHERE
        id IN ('{id_list}')
    """

    # Read geo data
    geo = pd.read_sql(sql, custom_uri)

    return pd.merge(data, geo, on="id_aviv", how="left")


def get_subregion_id_for_department(conn, department_code: str) -> int:
    """
    Get the subregion_id for a given department code (COG).

    Args:
        conn: Database connection
        department_code: Department code (e.g., "75" for Paris)

    Returns:
        subregion_id or None if not found
    """
    sql = """
    SELECT id, cog
    FROM geo.geo_place2
    WHERE
        cog = %(cog)s
        AND type = 30
        AND enabled = True
        AND active = True
    LIMIT 1
    """

    try:
        result = pd.read_sql(sql, conn, params={"cog": department_code})
        if not result.empty:
            return int(result.id.iloc[0])  # Convert to Python int
        return None
    except Exception as e:
        logger.warning(
            f"Could not find subregion for department {department_code}: {e}"
        )
        return None


def get_sales_for_subregion(
    conn, subregion_id: int, date_min: str, date_max: str = "2026-01-01"
) -> pd.DataFrame:
    """
    Fetch sales data for a given subregion.

    Args:
        conn: Database connection
        subregion_id: Subregion ID
        date_min: Start date (YYYY-MM-DD)
        date_max: End date (YYYY-MM-DD)

    Returns:
        DataFrame with sales data
    """
    sql = """
    SELECT
        past_sales.id,
        past_sales.address_id,
        address.street_id,
        address.subregion_id,
        past_sales.area,
        past_sales.floor,
        past_sales.energy_consumption_classification,
        past_sales.sale_agreement_date,
        past_sales.type
    FROM public.biz_past_sale AS past_sales
    LEFT JOIN geo.geo_address2 address ON (
        past_sales.address_id = address.id
        AND address.enabled = True
    )
    WHERE
        address.subregion_id = %(subregion_id)s
        AND past_sales.sale_agreement_date::DATE >= %(date_min)s
        AND past_sales.sale_agreement_date::DATE < %(date_max)s
    """

    df = pd.read_sql(
        sql,
        conn,
        params={
            "subregion_id": subregion_id,
            "date_min": date_min,
            "date_max": date_max,
        },
    ).sort_values(by=["sale_agreement_date"], ascending=False)

    # Map item types
    df["item_type"] = df["type"].map({1: "APARTMENT", 2: "HOUSE"})

    return df.dropna(subset=["item_type", "area"])


def load_dpe_data(department_code: str) -> pd.DataFrame:
    """
    Load DPE data from GCS for a given department.

    Args:
        department_code: Department code (e.g., "75")

    Returns:
        DataFrame with DPE data or None if not found
    """
    bucket_name = "ma-data-dev"
    file_name = f"ADEME/DPE/ADEME_GEOCODED_SUBREGION_CODE_{department_code}"

    if not gcs_file_exists(bucket_name, file_name):
        logger.warning(f"DPE data not found for department {department_code}")
        return None

    df = read_csv_from_gcs(bucket_name, file_name)

    # Ensure area column exists
    if "area" not in df.columns and "surface_habitable_logement" in df.columns:
        df["area"] = df["surface_habitable_logement"].apply(
            lambda x: round(x, 2) if pd.notna(x) else x
        )

    # Add legacy geo
    df = add_legacy_geo(df)

    return df


def analyze_results(master_df: pd.DataFrame, department_code: str) -> dict:
    """
    Analyze matching results and compute key metrics.

    Args:
        master_df: Results DataFrame from matching
        department_code: Department code

    Returns:
        Dictionary with metrics
    """
    total = len(master_df)

    if total == 0:
        return {
            "department": department_code,
            "total_sales": 0,
            "match_rate": 0,
            "disclosed_rate": 0,
            "error_rate": None,
            "advantageous_error_rate": None,
            "disadvantageous_error_rate": None,
        }

    # Match rate
    has_match = master_df["ademe_dpe"].notna().sum()
    match_rate = has_match / total

    # Disclosed rate
    has_disclosed = master_df["disclosed_dpe"].notna().sum()
    disclosed_rate = has_disclosed / total

    # Error analysis (where both disclosed and matched exist)
    both = master_df.dropna(subset=["disclosed_dpe", "ademe_dpe"])

    if len(both) == 0:
        return {
            "department": department_code,
            "total_sales": total,
            "match_rate": match_rate,
            "disclosed_rate": disclosed_rate,
            "validation_sample": 0,
            "error_rate": None,
            "advantageous_error_rate": None,
            "disadvantageous_error_rate": None,
        }

    # Error rates
    both["error"] = (both["disclosed_dpe"] != both["ademe_dpe"]).astype(float)
    both["positive_error"] = (
        both["disclosed_dpe"].str.lower() > both["ademe_dpe"].str.lower()
    ).astype(float)
    both["negative_error"] = (
        both["disclosed_dpe"].str.lower() < both["ademe_dpe"].str.lower()
    ).astype(float)

    error_rate = both["error"].sum() / len(both)
    advantageous_rate = both["positive_error"].sum() / len(both)
    disadvantageous_rate = both["negative_error"].sum() / len(both)

    return {
        "department": department_code,
        "total_sales": total,
        "matched_sales": has_match,
        "match_rate": match_rate,
        "disclosed_count": has_disclosed,
        "disclosed_rate": disclosed_rate,
        "validation_sample": len(both),
        "error_rate": error_rate,
        "advantageous_error_rate": advantageous_rate,
        "disadvantageous_error_rate": disadvantageous_rate,
    }


def run_department(
    conn, department_code: str, date_min: str, date_max: str, save_results: bool = True
) -> dict:
    """
    Run matching for a single department.

    Args:
        conn: Database connection
        department_code: Department code (e.g., "75")
        date_min: Start date
        date_max: End date
        save_results: Whether to save results to GCS

    Returns:
        Dictionary with results metrics
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"Processing department {department_code}")
    logger.info(f"{'='*70}")

    start_time = time.time()

    # Step 1: Get subregion ID
    subregion_id = get_subregion_id_for_department(conn, department_code)
    if subregion_id is None:
        logger.error(f"❌ Could not find subregion for department {department_code}")
        return {
            "department": department_code,
            "status": "error",
            "error": "subregion_not_found",
        }

    logger.info(f"   Subregion ID: {subregion_id}")

    # Step 2: Load DPE data
    dpe_df = load_dpe_data(department_code)
    if dpe_df is None or len(dpe_df) == 0:
        logger.error(f"❌ No DPE data available for department {department_code}")
        return {
            "department": department_code,
            "status": "error",
            "error": "no_dpe_data",
        }

    logger.info(f"   DPE records loaded: {len(dpe_df):,}")

    # Step 3: Get sales data
    # sales_df = get_sales_for_subregion(conn, subregion_id, date_min, date_max)
    sales_df = read_csv_from_gcs(
        bucket_name="ma-data-dev", file_name="EPC in AVM/data_house.csv"
    )
    sales_df = sales_df[sales_df.cog.astype(str) == department_code][
        [
            "address_id",
            "street_id",
            "floor",
            "area",
            "item_type",
            "cog",
            "source_record_id",
            "source_record_date",
        ]
    ].rename(
        columns={"source_record_id": "id", "source_record_date": "sale_agreement_date"}
    )
    sales_df["energy_consumption_classification"] = None
    sales_df["item_type"] = sales_df["item_type"].map(
        {"ITEM_TYPE.APARTMENT": "APARTMENT", "ITEM_TYPE.HOUSE": "HOUSE"}
    )

    if len(sales_df) == 0:
        logger.warning(f"⚠️ No sales data for department {department_code}")
        return {"department": department_code, "status": "no_sales", "total_sales": 0}

    logger.info(f"   Sales records loaded: {len(sales_df):,}")

    # Step 4: Run matching
    try:
        master, historic, distribution, statistics = match(
            df=sales_df,
            searcher_df=dpe_df,
            saved=save_results,
        )
        master["cog"] = department_code
    except Exception as e:
        logger.error(f"❌ Matching failed for department {department_code}: {e}")
        return {"department": department_code, "status": "error", "error": str(e)}

    # Step 5: Analyze results
    metrics = analyze_results(master, department_code)
    metrics["status"] = "success"
    metrics["processing_time_sec"] = round(time.time() - start_time, 1)

    logger.info(f"\n📊 Results for department {department_code}:")
    logger.info(f"   Total sales: {metrics['total_sales']:,}")
    logger.info(f"   Match rate: {metrics['match_rate']:.1%}")
    logger.info(f"   Disclosed rate: {metrics['disclosed_rate']:.1%}")
    if metrics.get("error_rate") is not None:
        logger.info(f"   Error rate: {metrics['error_rate']:.1%}")
        logger.info(f"   Advantageous errors: {metrics['advantageous_error_rate']:.1%}")
        logger.info(
            f"   Disadvantageous errors: {metrics['disadvantageous_error_rate']:.1%}"
        )
    logger.info(f"   Processing time: {metrics['processing_time_sec']}s")

    return metrics, master


def get_all_metropolitan_departments() -> list:
    """
    Get list of all metropolitan French department codes.

    Returns:
        List of department codes as strings
    """
    # Metropolitan France departments: 01-95 (excluding 20 which is Corsica, using 2A/2B)
    departments = [str(i).zfill(2) for i in range(1, 96) if i != 20]
    # Add Corsica
    departments.extend(["2A", "2B"])
    return sorted(departments)


def main():
    parser = argparse.ArgumentParser(
        description="Run DPE matching for French departments"
    )
    parser.add_argument(
        "--departments",
        type=str,
        default=None,
        help="Comma-separated list of department codes (e.g., '75,13,69'). Default: all metropolitan departments.",
    )
    parser.add_argument(
        "--date-min",
        type=str,
        default="2024-01-01",
        help="Start date for sales (YYYY-MM-DD). Default: 2024-01-01",
    )
    parser.add_argument(
        "--date-max",
        type=str,
        default="2025-05-01",
        help="End date for sales (YYYY-MM-DD). Default: 2025-05-01",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save results to GCS",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="department_report.csv",
        help="Output file for summary report. Default: department_report.csv",
    )

    args = parser.parse_args()

    # Determine departments to process
    if args.departments:
        departments = [d.strip() for d in args.departments.split(",")]
    else:
        departments = get_all_metropolitan_departments()

    logger.info("🚀 Starting DPE matching run")
    logger.info(f"   Departments to process: {len(departments)}")
    logger.info(f"   Date range: {args.date_min} to {args.date_max}")
    logger.info(f"   Save to GCS: {not args.no_save}")

    # Connect to database
    logger.info("📡 Connecting to database...")
    conn = get_db_connection()

    # Process each department
    all_results = []
    final = []
    successful = 0
    failed = 0

    total_start = time.time()

    for i, dept in enumerate(departments, 1):
        logger.info(f"\n[{i}/{len(departments)}] Processing department {dept}...")

        try:
            result, master = run_department(
                conn=conn,
                department_code=dept,
                date_min=args.date_min,
                date_max=args.date_max,
                save_results=not args.no_save,
            )
            all_results.append(result)
            final.append(master)

            if result.get("status") == "success":
                successful += 1
            else:
                failed += 1

        except Exception as e:
            logger.error(f"❌ Unexpected error for department {dept}: {e}")
            all_results.append({"department": dept, "status": "error", "error": str(e)})
            failed += 1

    # Concat
    pd.concat(final).to_csv("avm_data.csv", index=False)

    # Close database connection
    conn.close()

    # Generate summary report
    total_time = time.time() - total_start

    logger.info(f"\n{'='*70}")
    logger.info("📋 FINAL SUMMARY REPORT")
    logger.info(f"{'='*70}")
    logger.info(f"Total departments processed: {len(departments)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total processing time: {total_time/60:.1f} minutes")

    # Create summary DataFrame
    report_df = pd.DataFrame(all_results)

    # Print summary table
    if not report_df.empty:
        success_df = report_df[report_df["status"] == "success"].copy()

        if not success_df.empty:
            logger.info("\n📊 Successful Departments Summary:")
            logger.info(
                f"{'Dept':<6} {'Sales':>8} {'Match%':>8} {'Disclosed%':>10} {'Error%':>8} {'Adv.Err%':>10} {'Disadv.Err%':>12}"
            )
            logger.info("-" * 70)

            for _, row in success_df.iterrows():
                dept = row["department"]
                sales = row.get("total_sales", 0)
                match_rate = row.get("match_rate", 0) * 100
                disclosed_rate = row.get("disclosed_rate", 0) * 100
                error_rate = row.get("error_rate")
                adv_rate = row.get("advantageous_error_rate")
                disadv_rate = row.get("disadvantageous_error_rate")

                error_str = f"{error_rate*100:.1f}" if error_rate is not None else "N/A"
                adv_str = f"{adv_rate*100:.1f}" if adv_rate is not None else "N/A"
                disadv_str = (
                    f"{disadv_rate*100:.1f}" if disadv_rate is not None else "N/A"
                )

                logger.info(
                    f"{dept:<6} {sales:>8,} {match_rate:>7.1f}% {disclosed_rate:>9.1f}% {error_str:>8} {adv_str:>10} {disadv_str:>12}"
                )

            # Aggregate statistics
            logger.info("-" * 70)
            total_sales = success_df["total_sales"].sum()
            avg_match = success_df["match_rate"].mean() * 100
            avg_disclosed = success_df["disclosed_rate"].mean() * 100

            valid_errors = success_df.dropna(subset=["error_rate"])
            if len(valid_errors) > 0:
                avg_error = valid_errors["error_rate"].mean() * 100
                avg_adv = valid_errors["advantageous_error_rate"].mean() * 100
                avg_disadv = valid_errors["disadvantageous_error_rate"].mean() * 100
                logger.info(
                    f"{'TOTAL':<6} {total_sales:>8,} {avg_match:>7.1f}% {avg_disclosed:>9.1f}% {avg_error:>7.1f}% {avg_adv:>9.1f}% {avg_disadv:>11.1f}%"
                )
            else:
                logger.info(
                    f"{'TOTAL':<6} {total_sales:>8,} {avg_match:>7.1f}% {avg_disclosed:>9.1f}%"
                )

    # Save report
    report_df.to_csv(args.output, index=False)
    logger.info(f"\n💾 Report saved to: {args.output}")

    return report_df


if __name__ == "__main__":
    main()
