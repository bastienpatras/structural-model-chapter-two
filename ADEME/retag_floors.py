"""
Re-tag floor information for already geocoded DPE data.

This script reads existing geocoded data from GCS, re-extracts floor/loc/position
using the improved tagging regex, and exports back to GCS.
"""

import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import StringIO

import pandas as pd
from google.cloud import storage
from tagging import fast_extract_info
from tools import gcs_file_exists, read_csv_from_gcs


# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# GCS configuration
BUCKET_NAME = "ma-data-dev"
DPE_PATH_TEMPLATE = "ADEME/DPE/ADEME_GEOCODED_SUBREGION_CODE_{code}"
OUTPUT_PATH_TEMPLATE = "ADEME/DPE/ADEME_GEOCODED_SUBREGION_CODE_{code}"


def write_csv_to_gcs(bucket_name: str, blob_name: str, df: pd.DataFrame):
    """Write DataFrame to GCS, overwriting if exists."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv", timeout=600)
    logger.info(f"Exported to gs://{bucket_name}/{blob_name}")


def retag_single_department(dept_code: str, dry_run: bool = False) -> dict:
    """
    Re-tag floor information for a single department.

    Args:
        dept_code: Department code (e.g., "75", "2A", "971")
        dry_run: If True, don't write to GCS

    Returns:
        Dict with statistics
    """
    input_path = DPE_PATH_TEMPLATE.format(code=dept_code)
    output_path = OUTPUT_PATH_TEMPLATE.format(code=dept_code)

    stats = {
        "dept_code": dept_code,
        "status": "success",
        "total_records": 0,
        "floors_before": 0,
        "floors_after": 0,
        "new_floors_found": 0,
        "error": None,
    }

    try:
        # Check if file exists
        if not gcs_file_exists(BUCKET_NAME, input_path):
            logger.warning(f"File not found: gs://{BUCKET_NAME}/{input_path}")
            stats["status"] = "not_found"
            return stats

        # Read existing data
        logger.info(f"Reading gs://{BUCKET_NAME}/{input_path}")
        data = read_csv_from_gcs(BUCKET_NAME, input_path)
        stats["total_records"] = len(data)

        # Count floors before re-tagging
        if "floor" in data.columns:
            stats["floors_before"] = data["floor"].notna().sum()

        # Re-extract floor information using improved regex
        logger.info(f"Re-tagging {len(data)} records for department {dept_code}...")

        if "complement_adresse_logement" not in data.columns:
            logger.error(
                f"Column 'complement_adresse_logement' not found in {input_path}"
            )
            stats["status"] = "missing_column"
            return stats

        # Apply improved tagging
        results = data["complement_adresse_logement"].astype(str).map(fast_extract_info)
        data[["floor", "loc", "position"]] = pd.DataFrame(
            results.tolist(), index=data.index
        )

        # Count floors after re-tagging
        stats["floors_after"] = data["floor"].notna().sum()
        stats["new_floors_found"] = stats["floors_after"] - stats["floors_before"]

        logger.info(
            f"Department {dept_code}: "
            f"{stats['floors_before']} -> {stats['floors_after']} floors "
            f"(+{stats['new_floors_found']} new)"
        )

        # Export to GCS
        if not dry_run:
            write_csv_to_gcs(BUCKET_NAME, output_path, data)
        else:
            logger.info(f"[DRY RUN] Would export to gs://{BUCKET_NAME}/{output_path}")

    except Exception as e:
        logger.exception(f"Error processing department {dept_code}: {e}")
        stats["status"] = "error"
        stats["error"] = str(e)

    return stats


def retag_all_departments(
    dry_run: bool = False,
    max_workers: int = 4,
    departments: list = None,
):
    """
    Re-tag floor information for all French departments.

    Args:
        dry_run: If True, don't write to GCS
        max_workers: Number of parallel workers
        departments: List of department codes to process (None = all)
    """
    # All French department codes
    if departments is None:
        departments = (
            [f"{i:02d}" for i in range(1, 20)]  # 01-19
            + ["2A", "2B"]  # Corsica
            + [f"{i:02d}" for i in range(21, 96)]  # 21-95
            + ["971", "972", "973", "974", "976"]  # Overseas
        )

    logger.info(f"Starting re-tagging for {len(departments)} departments...")
    logger.info(f"Dry run: {dry_run}")
    logger.info("=" * 60)

    all_stats = []

    # Process departments in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_dept = {
            executor.submit(retag_single_department, dept, dry_run): dept
            for dept in departments
        }

        for future in as_completed(future_to_dept):
            dept = future_to_dept[future]
            try:
                stats = future.result()
                all_stats.append(stats)
            except Exception as e:
                logger.exception(f"Unexpected error for department {dept}: {e}")
                all_stats.append(
                    {
                        "dept_code": dept,
                        "status": "error",
                        "error": str(e),
                    }
                )

    # Summary
    print("\n" + "=" * 60)
    print("RE-TAGGING SUMMARY")
    print("=" * 60)

    total_records = sum(s.get("total_records", 0) for s in all_stats)
    total_before = sum(s.get("floors_before", 0) for s in all_stats)
    total_after = sum(s.get("floors_after", 0) for s in all_stats)
    total_new = sum(s.get("new_floors_found", 0) for s in all_stats)

    success_count = sum(1 for s in all_stats if s["status"] == "success")
    not_found_count = sum(1 for s in all_stats if s["status"] == "not_found")
    error_count = sum(1 for s in all_stats if s["status"] == "error")

    print(f"Departments processed: {success_count}/{len(departments)}")
    print(f"  - Success: {success_count}")
    print(f"  - Not found: {not_found_count}")
    print(f"  - Errors: {error_count}")
    print()
    print(f"Total records: {total_records:,}")
    print(f"Floors before: {total_before:,}")
    print(f"Floors after:  {total_after:,}")
    print(
        f"New floors found: +{total_new:,} ({total_new / total_before * 100:.1f}% improvement)"
        if total_before > 0
        else ""
    )
    print("=" * 60)

    # Show errors if any
    errors = [s for s in all_stats if s["status"] == "error"]
    if errors:
        print("\nErrors:")
        for s in errors:
            print(f"  - {s['dept_code']}: {s.get('error', 'Unknown error')}")

    # Show departments not found
    not_found = [s for s in all_stats if s["status"] == "not_found"]
    if not_found:
        print(f"\nDepartments not found in GCS: {[s['dept_code'] for s in not_found]}")

    return all_stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Re-tag floor information for geocoded DPE data"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write to GCS, just show what would be done",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)",
    )
    parser.add_argument(
        "--departments",
        nargs="+",
        help="Specific departments to process (e.g., 75 92 93). Default: all",
    )

    args = parser.parse_args()

    retag_all_departments(
        dry_run=args.dry_run,
        max_workers=args.workers,
        departments=args.departments,
    )
