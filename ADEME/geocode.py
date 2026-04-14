import asyncio
import logging
import time
import warnings
from collections import deque

import aiohttp
import numpy as np
import pandas as pd
import psycopg2
from fetch import master_fetching
from tagging import fast_extract_info
from tools import export_to_gcs, read_csv_from_gcs


warnings.filterwarnings("ignore")

# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Adaptive Rate Limiter
async def adaptive_rate_limiter(request_timestamps, max_requests_per_second):
    """Ensures we do not exceed API rate limits by dynamically adjusting request speed."""
    now = time.time()

    # Remove old timestamps beyond 1 second
    while request_timestamps and now - request_timestamps[0] > 1:
        request_timestamps.popleft()

    if len(request_timestamps) >= max_requests_per_second:
        wait_time = 1 - (now - request_timestamps[0])
        logger.warning(f"⏳ Rate limit reached, waiting {wait_time:.3f} seconds...")
        await asyncio.sleep(wait_time)

    request_timestamps.append(time.time())


# Fetch Address with Adaptive Rate Limiting and Retries
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
    """Handles API request, retries on failure, and adapts to rate limits."""
    if not params.get("address"):
        logger.warning("⚠️ Empty address encountered, skipping request.")
        return None

    async with semaphore:
        for attempt in range(max_retries + 1):
            await adaptive_rate_limiter(
                request_timestamps, max_requests_per_second
            )  # Enforce adaptive rate limit

            try:
                async with session.get(
                    url, params=params, headers=headers, timeout=10
                ) as response:
                    if response.status == 200:
                        remaining_addresses[
                            0
                        ] -= 1  # Decrease the count of remaining addresses
                        logger.info(
                            f"✅ Successfully fetched data for {params['address']} | {remaining_addresses[0]} remaining"
                        )
                        return await response.json()

                    elif response.status == 429:  # Too Many Requests
                        wait_time = 2**attempt  # Exponential Backoff (2s, 4s, 8s)
                        logger.warning(
                            f"🚦 HTTP 429 Too Many Requests for {params['address']}, retrying in {wait_time}s ({attempt + 1}/{max_retries})..."
                        )
                        await asyncio.sleep(wait_time)

                    else:
                        logger.error(
                            f"❌ Failed request for {params['address']}, HTTP Status: {response.status}"
                        )
                        return None

            except aiohttp.ClientError as e:
                logger.exception(
                    f"🌐 Network error while fetching {params['address']}: {e}"
                )

            if attempt < max_retries:
                await asyncio.sleep(2**attempt)  # Exponential Backoff

        logger.error(f"❌ Exhausted retries for {params['address']}, skipping.")
        return None


# Geocode Addresses with Rolling Rate Limit
async def geocode_addresses(
    address_batch, url, API_key, max_requests_per_second=100, semaphore_limit=50
):
    """Processes a batch of addresses asynchronously while adapting to API rate limits."""
    if not isinstance(address_batch, list):
        logger.error("🚨 address_batch must be a list of addresses")
        raise ValueError("address_batch must be a list of addresses")

    address_batch = [addr for addr in address_batch if pd.notna(addr)]
    headers = {"X-Api-Key": API_key}
    semaphore = asyncio.Semaphore(semaphore_limit)
    request_timestamps = deque()  # Track request timestamps
    remaining_addresses = [
        len(address_batch)
    ]  # Mutable counter to track remaining addresses

    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(
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
            for addr in address_batch
            if addr
        ]

        responses = await asyncio.gather(*tasks)

    logger.info("🎯 Finished geocoding all addresses.")
    return responses


def process_responses(responses, address_batch):
    """Processes API responses into a DataFrame and lists failed addresses."""
    records = []
    failed_addresses = []

    for i, (response, address) in enumerate(zip(responses, address_batch)):
        if response:
            try:
                aviv_items = response.get("items", {}).get("aviv", [])
                if aviv_items:  # Check that the list is not empty
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
                        f"❌ No 'aviv' items found in response for {address}."
                    )
                    failed_addresses.append(address)
            except Exception as e:
                logger.exception(f"⚠️ Error processing response for {address}: {e}")
                failed_addresses.append(address)
        else:
            logger.warning(
                f"❌ No response received for {address}, adding to failed list."
            )
            failed_addresses.append(address)

    master_table = pd.DataFrame(records).drop_duplicates()

    logger.info(
        f"📊 Geocoding complete. {len(failed_addresses)}/{len(address_batch)} = "
        f"{round(len(failed_addresses)/len(address_batch)*100, 2)}% of addresses failed."
    )
    return master_table, failed_addresses


# Run the async function inside an event loop
async def master_geocode(data: pd.DataFrame):
    """
    Asynchronously geocodes a batch of addresses and processes the responses.

    This function takes a Pandas DataFrame containing addresses, sends them
    to a geocoding API, processes the responses, and returns a master table
    of geocoded addresses along with any failed addresses.

    Args:
        data (pd.DataFrame): A DataFrame containing address data with the column
                             "Adresse_(BAN)" holding the addresses to be geocoded.

    Returns:
        Tuple[pd.DataFrame, List[str]]:
            - A DataFrame (`master_table`) with the successfully geocoded addresses.
            - A list of failed addresses that could not be geocoded.

    Logs:
        - Logs the number of addresses being processed.
        - Logs the percentage of failed addresses after geocoding.

    Note:
        - The function utilizes an asynchronous geocoding API call.
        - The API key and endpoint are hardcoded; ensure security best practices
          for handling sensitive data.
    """
    logger.info(f"🏡 Processing {len(data['ademe_address'].to_list())} addresses...")

    # Collect responses given address batch
    responses = await geocode_addresses(
        address_batch=data["ademe_address"].to_list(),
        url="https://geocoding-api.cosmic-bullfrog-live.aws.aviv.eu/v1/geocode/singleline",
        API_key="KJ2hnPD9EbafPYNsUsFpk8OhNWYCckWg8OzG5jSo",
    )

    # Process the responses
    master_table, failed_addresses = process_responses(
        responses, data["ademe_address"].to_list()
    )

    # Print loggers assessing geocoding efficiency
    logger.info(
        f"🚨 Failed Addresses: {round(len(failed_addresses)/len(data['ademe_address'].to_list())*100, 2)}%"
    )

    return master_table, failed_addresses


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


def run_geocoding(
    start_date: str,
    end_date: str,
    api_url: str,
    query_field: str,
    query_geo: int,
    dataset=None,
):
    """
    Fetches address data for a given date range and performs geocoding.

    This function retrieves address data using `master_fetching` for the specified date range.
    It then runs the geocoding process asynchronously.

    Args:
        start_date (str): The start date of the data fetching period in 'YYYY-MM-DD' format.
        end_date (str): The end date of the data fetching period in 'YYYY-MM-DD' format.

    Returns:
        tuple: A tuple containing:
            - master_table (pd.DataFrame): The processed DataFrame with geocoded addresses.
            - failed_addresses (list): A list of addresses that failed to be geocoded.
    """

    columns_to_keep = [
        "numero_dpe",
        "numero_dpe_immeuble_associe",
        "numero_dpe_remplace",
        "ademe_address",
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

    # Fetches EPCs from ADEME directly or from GCS
    if dataset is not None:
        logger.info(
            f"Data is collected from a GCS file: 'ADEME/RAW/ADEME_RAW_SUBREGION_CODE_{query_geo}'"
        )
        data = read_csv_from_gcs(
            bucket_name="ma-data-dev",
            file_name=f"ADEME/RAW/ADEME_RAW_SUBREGION_CODE_{query_geo}",
        )[columns_to_keep].drop_duplicates()
        data.ademe_address = data.adresse_ban
    else:
        data = master_fetching(
            start_date=start_date,
            end_date=end_date,
            api_url=api_url,
            query_field=query_field,
            query_geo=query_geo,
        )[columns_to_keep].drop_duplicates()
        data.ademe_address = data.adresse_ban

    # Geocode EPCs
    master_table, failed_addresses = asyncio.run(
        master_geocode(
            data=data.drop_duplicates(subset=["ademe_address"]),
        )
    )

    # Export data to GCS
    export_to_gcs(
        bucket_name="ma-data-dev",
        blob_name=f"ADEME/GEOCODED/ADDRESSES_SUBREGION_CODE_{query_geo}",
        new_df=master_table,
    )

    # Cast string format
    data["ademe_address"] = data["ademe_address"].astype(str)
    master_table["ademe_address"] = master_table["ademe_address"].astype(str)

    # Merge with fetched data
    logger.info(f"🏡 Adding geocoding ids to {len(data)} rows...")

    data = pd.merge(
        data,
        master_table,
        on="ademe_address",
        how="left",
    )

    # Clear RAM
    del master_table

    logger.info(f"🏡 Adding legacy georef to {len(data)} rows...")

    # data = add_legacy_geo(
    #     data=data,
    #     # uri="DATABASE_LISTING_URI"
    # )

    data = data.dropna(subset=["surface_habitable_logement"])
    data["area"] = data.surface_habitable_logement.apply(lambda x: round(x, 2))

    logger.info("🏡 Collecting floors...")

    # Vectorized unpacking into DataFrame
    results = data["complement_adresse_logement"].astype(str).map(fast_extract_info)
    data[["floor", "loc", "position"]] = pd.DataFrame(
        results.tolist(), index=data.index
    )

    logger.info("✅ Floors collected...")

    # Export data to GCS
    export_to_gcs(
        bucket_name="ma-data-dev",
        blob_name=f"ADEME/DPE/ADEME_GEOCODED_SUBREGION_CODE_{query_geo}",
        new_df=data,
    )

    # Export data to GCS
    export_to_gcs(
        bucket_name="ma-data-dev",
        blob_name=f"ADEME/FAILED_ADDRESSES/ADEME_GEOCODED_SUBREGION_CODE_{query_geo}",
        new_df=pd.DataFrame(failed_addresses, columns=["failed_addresses"]),
    )

    return data.dropna(subset=["floor"]), failed_addresses


for geo in [i for i in range(95, 97)]:
    master_table, failed_addresses = run_geocoding(
        dataset=None,
        start_date="2021-07-01",
        end_date="2025-05-01",
        api_url="https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines",
        query_field="date_reception_dpe",
        query_geo=str(geo),
    )
