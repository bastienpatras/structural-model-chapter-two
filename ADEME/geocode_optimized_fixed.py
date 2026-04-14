"""
Optimized geocoding module with alignment fix.

This module fixes the critical zip alignment bug in geocode.py
"""

import asyncio
import logging
import time
import warnings
from collections import deque

import aiohttp
import numpy as np
import pandas as pd
from fetch import master_fetching
from tagging import fast_extract_info
from tools import export_to_gcs


warnings.filterwarnings("ignore")

# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# FIXED ASYNC GEOCODING (with alignment fix)
# =============================================================================


async def adaptive_rate_limiter(request_timestamps, max_requests_per_second):
    """Ensures we do not exceed API rate limits."""
    now = time.time()

    while request_timestamps and now - request_timestamps[0] > 1:
        request_timestamps.popleft()

    if len(request_timestamps) >= max_requests_per_second:
        wait_time = 1 - (now - request_timestamps[0])
        logger.warning(f"⏳ Rate limit reached, waiting {wait_time:.3f} seconds...")
        await asyncio.sleep(wait_time)

    request_timestamps.append(time.time())


async def fetch_address(
    session,
    url,
    params,
    headers,
    semaphore,
    request_timestamps,
    max_requests_per_second,
    remaining_addresses,
    max_retries=3,
):
    """Handles API request with retries."""
    if not params.get("address"):
        logger.warning("⚠️ Empty address encountered, returning None")
        return None

    async with semaphore:
        for attempt in range(max_retries + 1):
            await adaptive_rate_limiter(request_timestamps, max_requests_per_second)

            try:
                async with session.get(
                    url, params=params, headers=headers, timeout=10
                ) as response:
                    if response.status == 200:
                        remaining_addresses[0] -= 1
                        logger.info(
                            f"✅ Fetched {params['address'][:50]}... | {remaining_addresses[0]} remaining"
                        )
                        return await response.json()

                    elif response.status == 429:
                        wait_time = 2**attempt
                        logger.warning(
                            f"🚦 HTTP 429 for {params['address'][:50]}..., "
                            f"retrying in {wait_time}s ({attempt + 1}/{max_retries})..."
                        )
                        await asyncio.sleep(wait_time)

                    else:
                        logger.error(
                            f"❌ Failed for {params['address'][:50]}..., "
                            f"HTTP Status: {response.status}"
                        )
                        return None

            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Timeout for {params['address'][:50]}...")
            except aiohttp.ClientError as e:
                logger.exception(
                    f"🌐 Network error for {params['address'][:50]}...: {e}"
                )

            if attempt < max_retries:
                await asyncio.sleep(2**attempt)

        logger.error(f"❌ Exhausted retries for {params['address'][:50]}..., skipping.")
        return None


async def geocode_addresses_fixed(
    address_batch, url, API_key, max_requests_per_second=100, semaphore_limit=50
):
    """
    FIXED: Processes addresses while maintaining 1:1 alignment.

    Key fix: Creates tasks for ALL addresses (including None/empty),
    so responses align perfectly with input.
    """
    if not isinstance(address_batch, list):
        logger.error("🚨 address_batch must be a list of addresses")
        raise ValueError("address_batch must be a list of addresses")

    headers = {"X-Api-Key": API_key}
    semaphore = asyncio.Semaphore(semaphore_limit)
    request_timestamps = deque()

    # Count valid addresses only
    valid_count = sum(1 for addr in address_batch if pd.notna(addr) and addr)
    remaining_addresses = [valid_count]

    logger.info(
        f"🚀 Geocoding {valid_count} valid addresses (out of {len(address_batch)} total)"
    )

    async with aiohttp.ClientSession() as session:
        tasks = []
        for addr in address_batch:
            # FIX: Create task even for None/empty to maintain alignment
            if pd.notna(addr) and addr:
                task = asyncio.create_task(
                    fetch_address(
                        session,
                        url,
                        {"country": "FR", "address": addr},
                        headers,
                        semaphore,
                        request_timestamps,
                        max_requests_per_second,
                        remaining_addresses,
                    )
                )
            else:
                # Placeholder task that returns None
                async def return_none():
                    return None

                task = asyncio.create_task(return_none())

            tasks.append(task)

        responses = await asyncio.gather(*tasks)

    logger.info("🎯 Finished geocoding all addresses.")

    # Validate alignment
    if len(responses) != len(address_batch):
        logger.error(
            f"❌ ALIGNMENT ERROR: {len(responses)} responses for {len(address_batch)} addresses!"
        )
        raise ValueError(
            f"Response/address count mismatch: {len(responses)} != {len(address_batch)}"
        )

    return responses


def process_responses_fixed(responses, address_batch):
    """
    FIXED: Processes responses with guaranteed alignment.

    Now validates that response count matches address count.
    """
    if len(responses) != len(address_batch):
        raise ValueError(
            f"Response/address alignment error: {len(responses)} responses "
            f"for {len(address_batch)} addresses"
        )

    records = []
    failed_addresses = []

    for i, (response, address) in enumerate(zip(responses, address_batch)):
        if response:
            try:
                aviv_items = response.get("items", {}).get("aviv", [])
                if aviv_items:
                    item = aviv_items[0].get("match", {})
                    records.append(
                        {
                            "id_aviv": item.get("id", np.nan),
                            "ademe_address": address,
                            "match_name": item.get("match_name", np.nan),
                            "confidence_score": item.get("confidence_score", np.nan),
                            "type_key": item.get("type_key", np.nan),
                            "row_id": i,
                        }
                    )
                else:
                    logger.warning(
                        f"❌ No aviv items for {address[:50] if address else 'None'}..."
                    )
                    failed_addresses.append(address)
            except Exception as e:
                logger.exception(
                    f"⚠️ Error processing {address[:50] if address else 'None'}...: {e}"
                )
                failed_addresses.append(address)
        else:
            if pd.notna(address) and address:  # Only log for valid addresses
                logger.warning(f"❌ No response for {address[:50]}...")
                failed_addresses.append(address)

    master_table = pd.DataFrame(records).drop_duplicates(subset=["ademe_address"])

    success_rate = (
        (len(address_batch) - len(failed_addresses)) / len(address_batch) * 100
        if len(address_batch) > 0
        else 0
    )
    logger.info(
        f"📊 Geocoding complete. {len(failed_addresses)}/{len(address_batch)} = "
        f"{success_rate:.1f}% success rate"
    )

    return master_table, failed_addresses


async def master_geocode_fixed(data: pd.DataFrame, api_key: str):
    """
    FIXED: Geocodes addresses with guaranteed alignment.
    """
    logger.info(f"🏡 Processing {len(data)} addresses...")

    # Get address list
    address_list = data["ademe_address"].to_list()

    # Store original count for validation
    # original_count = len(address_list)

    # Geocode with fixed function
    responses = await geocode_addresses_fixed(
        address_batch=address_list,
        url="https://geocoding-api.cosmic-bullfrog-live.aws.aviv.eu/v1/geocode/singleline",
        API_key=api_key,
    )

    # Process responses
    master_table, failed_addresses = process_responses_fixed(responses, address_list)

    logger.info(
        f"✅ Geocoding complete: {len(master_table)} successful, {len(failed_addresses)} failed"
    )

    return master_table, failed_addresses


# =============================================================================
# MAIN GEOCODING WORKFLOW
# =============================================================================


def run_geocoding_fixed(
    start_date: str,
    end_date: str,
    api_url: str,
    query_field: str,
    query_geo: int,
    api_key: str,
    dataset=None,
):
    """
    Geocoding with alignment fix.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        api_url: ADEME API URL
        query_field: Query field (usually "date_reception_dpe")
        query_geo: Department code
        api_key: Aviv geocoding API key
        dataset: If provided, reads from GCS

    Returns:
        Tuple of (geocoded_dataframe, failed_addresses)
    """
    logger.info(f"{'='*60}")
    logger.info("Starting geocoding with alignment fix")
    logger.info(f"  Department: {query_geo}")
    logger.info(f"  Date range: {start_date} to {end_date}")
    logger.info(f"{'='*60}")

    columns_to_keep = [
        "numero_dpe",
        "numero_dpe_immeuble_associe",
        "numero_dpe_remplace",
        "adresse_ban",
        "code_departement_ban",
        "annee_construction",
        "surface_habitable_logement",
        "numero_etage_appartement",
        "date_reception_dpe",
        "date_visite_diagnostiqueur",
        "modele_dpe",
        "etiquette_dpe",
        "etiquette_ges",
        "statut_geocodage",
        "complement_adresse_logement",
        "complement_adresse_batiment",
    ]

    # Fetch ADEME data
    if dataset is not None:
        logger.info("📥 Reading from GCS...")
        from tools import read_csv_from_gcs

        data = read_csv_from_gcs(
            bucket_name="ma-data-dev",
            file_name=f"ADEME/RAW/ADEME_RAW_SUBREGION_CODE_{query_geo}",
        )[columns_to_keep].drop_duplicates()
    else:
        logger.info("📥 Fetching from ADEME API...")
        data = master_fetching(
            start_date=start_date,
            end_date=end_date,
            api_url=api_url,
            query_field=query_field,
            query_geo=query_geo,
        )

        # Only keep columns that actually exist in the data
        available_cols = [col for col in columns_to_keep if col in data.columns]
        data = data[available_cols].drop_duplicates()

    logger.info(f"✅ Fetched {len(data)} DPE records")

    # Set address
    data["ademe_address"] = data["adresse_ban"].astype(str)

    # Store original row count for validation
    original_count = len(data)

    # Geocode unique addresses
    unique_addresses = data.drop_duplicates(subset=["ademe_address"])
    logger.info(f"🗺️ Geocoding {len(unique_addresses)} unique addresses")

    master_table, failed_addresses = asyncio.run(
        master_geocode_fixed(
            data=unique_addresses,
            api_key=api_key,
        )
    )

    # Export geocoded addresses
    try:
        export_to_gcs(
            bucket_name="ma-data-dev",
            blob_name=f"ADEME/GEOCODED/ADDRESSES_SUBREGION_CODE_{query_geo}",
            new_df=master_table,
        )
        logger.info("✅ Exported geocoded addresses to GCS")
    except Exception as e:
        logger.error(f"❌ Failed to export to GCS: {e}")

    # Merge with original data
    logger.info("🔗 Merging geocoding results...")

    data["ademe_address"] = data["ademe_address"].astype(str)
    master_table["ademe_address"] = master_table["ademe_address"].astype(str)

    data = pd.merge(
        data,
        master_table,
        on="ademe_address",
        how="left",
    )

    # Validate merge didn't change row count
    if len(data) != original_count:
        logger.error(
            f"❌ MERGE ERROR: Row count changed from {original_count} to {len(data)}!"
        )
        raise ValueError(
            f"Merge caused row count change: {original_count} -> {len(data)}"
        )

    logger.info(f"✅ Merge validation passed: {len(data)} rows maintained")

    # Clear RAM
    del master_table

    # Process area and floor
    data = data.dropna(subset=["surface_habitable_logement"])
    data["area"] = data["surface_habitable_logement"].apply(lambda x: round(x, 2))

    logger.info("🏢 Extracting floor information...")
    results = data["complement_adresse_logement"].astype(str).map(fast_extract_info)
    data[["floor", "loc", "position"]] = pd.DataFrame(
        results.tolist(), index=data.index
    )

    logger.info("✅ Floor extraction complete")

    # Export final data
    try:
        export_to_gcs(
            bucket_name="ma-data-dev",
            blob_name=f"ADEME/DPE/ADEME_GEOCODED_SUBREGION_CODE_{query_geo}",
            new_df=data,
        )
        logger.info("✅ Exported final data to GCS")
    except Exception as e:
        logger.error(f"❌ Failed to export final data: {e}")

    # Export failed addresses
    try:
        export_to_gcs(
            bucket_name="ma-data-dev",
            blob_name=f"ADEME/FAILED_ADDRESSES/ADEME_GEOCODED_SUBREGION_CODE_{query_geo}",
            new_df=pd.DataFrame(failed_addresses, columns=["failed_addresses"]),
        )
        logger.info("✅ Exported failed addresses to GCS")
    except Exception as e:
        logger.error(f"❌ Failed to export failed addresses: {e}")

    # Final summary
    final_count = len(data.dropna(subset=["floor"]))
    geocoded_count = data["id_aviv"].notna().sum()

    logger.info(f"\n{'='*60}")
    logger.info("Geocoding complete!")
    logger.info(f"  Total records: {len(data)}")
    logger.info(
        f"  Successfully geocoded: {geocoded_count} ({geocoded_count/len(data)*100:.1f}%)"
    )
    logger.info(f"  Failed addresses: {len(failed_addresses)}")
    logger.info(f"  Final dataset (with floors): {final_count}")
    logger.info(f"{'='*60}\n")

    return data.dropna(subset=["floor"]), failed_addresses


# =============================================================================
# RUN FOR ALL FRENCH DEPARTMENTS
# =============================================================================

if __name__ == "__main__":
    import os

    # Get API key from environment
    api_key = os.getenv("AVIV_GEOCODING_API_KEY")

    if not api_key:
        print("❌ ERROR: AVIV_GEOCODING_API_KEY environment variable not set!")
        print("Please set it with: export AVIV_GEOCODING_API_KEY='your-key-here'")
        exit(1)

    # All French department codes
    # Metropolitan: 01-19, 21-95 (20 is Corsica: 2A, 2B)
    # Overseas: 971, 972, 973, 974, 976
    departments = (
        [f"{i:02d}" for i in range(1, 20)]
        + ["2A", "2B"]  # 01-19
        + [f"{i:02d}" for i in range(21, 96)]  # Corsica
        + ["971", "972", "973", "974", "976"]  # 21-95  # Overseas
    )

    total_records = 0
    total_geocoded = 0
    total_failed = 0
    failed_departments = []

    logger.info(
        f"🚀 Starting geocoding for all {len(departments)} French departments..."
    )
    logger.info("=" * 60)

    for i, dept in enumerate(departments, 1):
        logger.info(f"\n📍 Processing department {dept} ({i}/{len(departments)})...")

        try:
            data, failed = run_geocoding_fixed(
                start_date="2021-07-01",
                end_date="2025-01-01",
                api_url="https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines",
                query_field="date_reception_dpe",
                query_geo=dept,
                api_key=api_key,
                dataset=None,
            )

            records = len(data)
            geocoded = data["id_aviv"].notna().sum()

            total_records += records
            total_geocoded += geocoded
            total_failed += len(failed)

            # Check for alignment issues
            duplicates = data[data.duplicated(subset=["numero_dpe"], keep=False)]

            print(
                f"✅ Department {dept}: {records} records, {geocoded} geocoded, {len(duplicates)} duplicates"
            )

            if len(duplicates) > 0:
                print(f"   ⚠️ WARNING: Found {len(duplicates)} duplicate records!")

        except Exception as e:
            logger.error(f"❌ Failed to process department {dept}: {e}")
            failed_departments.append(dept)
            continue

    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL SUMMARY")
    print("=" * 60)
    print(
        f"   Total departments processed: {len(departments) - len(failed_departments)}/{len(departments)}"
    )
    print(f"   Total records: {total_records}")
    print(f"   Total geocoded: {total_geocoded}")
    print(f"   Total failed addresses: {total_failed}")
    if failed_departments:
        print(f"   ❌ Failed departments: {failed_departments}")
    print("=" * 60)
