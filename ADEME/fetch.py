import asyncio
import json
import logging
import time
import urllib.parse
from collections import deque
from datetime import datetime, timedelta

import aiohttp
import asyncpg
import pandas as pd
from fake_useragent import UserAgent
from tools import export_to_gcs


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

API_URL = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines"

# Rate limiting settings
MAX_REQUESTS_PER_SECOND = 1
# SEMAPHORE = asyncio.BoundedSemaphore(MAX_REQUESTS_PER_SECOND)
request_timestamps = deque(maxlen=MAX_REQUESTS_PER_SECOND)
failed_requests = []
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 5


# Default database configuration
DEFAULT_DB_CONFIG = {
    "user": "customdb",
    "password": "****",  # Replace with actual password
    "database": "listing_dev",
    # "host": "custom-db-phd-bastien-listing-dev-1c-001",
    "host": "localhost",
    "port": 1111,
}


# Initialize fake User-Agent
ua = UserAgent()


def get_random_headers():
    """Returns a random User-Agent header for each request."""
    return {"User-Agent": ua.random, "Accept": "application/json"}


async def enforce_rate_limit():
    """Ensures API calls do not exceed the allowed rate."""
    while len(request_timestamps) >= MAX_REQUESTS_PER_SECOND:
        now = asyncio.get_running_loop().time()
        wait_time = max(0, 1 - (now - request_timestamps[0]))
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        request_timestamps.popleft()


async def fetch_data(
    session, start_date, end_date, size, api_url, query_field, query_geo, semaphore
):
    """Fetch paginated data from API with correct 'after' parameter handling."""
    query = f"{query_field}:[{start_date} TO {end_date}]"
    if query_geo:
        query += f" AND code_departement_ban:{str(query_geo)}"
    all_results = []
    after = None
    retries = 0
    timeout = aiohttp.ClientTimeout(total=60)
    used_afters = set()  # Track seen cursors

    async with semaphore:
        while True:
            await enforce_rate_limit()
            params = {"qs": query, "size": size}
            if after:
                if after in used_afters:
                    logging.warning(
                        f"🔁 Already tried after={after}, skipping to avoid loop."
                    )
                    break
                used_afters.add(after)
                params["after"] = after

            headers = get_random_headers()

            logging.info(
                f"🚀 Fetching {start_date} → {end_date} (size={size}, after={params.get('after')})"
            )

            try:
                async with session.get(
                    api_url, params=params, headers=headers, timeout=timeout
                ) as response:
                    if response.status != 200:
                        logging.error(
                            f"❌ HTTP {response.status} error for {start_date} → {end_date}"
                        )
                        return all_results

                    data = await response.json()
                    results = data.get("results", [])
                    if not results:
                        logging.info("🚪 No new records fetched, stopping pagination.")
                        break

                    all_results.extend(results)
                    logging.info(
                        f"✅ {len(results)} records fetched (Total: {len(all_results)})"
                    )

                    next_page = data.get("next")
                    if next_page:
                        parsed_url = urllib.parse.urlparse(next_page)
                        query_params = urllib.parse.parse_qs(parsed_url.query)
                        if "after" in query_params:
                            after = query_params["after"][0]
                            retries = 0  # Reset retry counter on success
                        else:
                            break
                    else:
                        break

            except asyncio.TimeoutError:
                retries += 1
                wait_time = min(2**retries, 60)
                logging.warning(
                    f"⏳ Timeout {retries}/{MAX_RETRIES} for after={after}, retrying in {wait_time}s..."
                )
                if retries >= MAX_RETRIES:
                    logging.error(
                        f"🛑 Giving up on 'after'={after} for {start_date} → {end_date}, skipping it."
                    )
                    after = None  # Skip this cursor and continue (fetch what we can)
                    retries = 0
                    continue
                await asyncio.sleep(wait_time + 0.5)  # Slight jitter to avoid hammering
            except aiohttp.ClientError as e:
                logging.error(f"❌ HTTP Error: {e}")
                return all_results
            except Exception as e:
                logging.error(f"❌ Unknown Error: {e}")
                return all_results

    return all_results


async def query_dpe_data_df(
    session, start_date, end_date, size, api_url, batch_days, query_field, query_geo
):
    """Fetch API data in parallel while retrying failed requests."""
    all_data = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

    semaphore = asyncio.BoundedSemaphore(MAX_REQUESTS_PER_SECOND)

    tasks = []
    while current_date < end_date_dt:
        batch_end = min(current_date + timedelta(days=batch_days), end_date_dt)
        tasks.append(
            fetch_data(
                session,
                current_date.strftime("%Y-%m-%d"),
                batch_end.strftime("%Y-%m-%d"),
                size,
                api_url,
                query_field,
                query_geo,
                semaphore,
            )
        )
        current_date = batch_end

    logging.info(f"⏳ Launching {len(tasks)} requests with rate limiting...")
    results = await asyncio.gather(*tasks)
    for data in results:
        all_data.extend(data)

    if failed_requests:
        logging.warning(
            f"⚠️ Retrying {len(failed_requests)} failed requests with a new session..."
        )
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit_per_host=5)
        ) as retry_session:
            retry_tasks = [
                fetch_data(
                    retry_session,
                    start,
                    end,
                    size,
                    api_url,
                    query_field,
                    query_geo,
                    semaphore,
                )
                for start, end in failed_requests
            ]
            retry_results = await asyncio.gather(*retry_tasks)
            for data in retry_results:
                all_data.extend(data)

    return clean_dataframe(pd.DataFrame(all_data))


def clean_dataframe(df):
    """Removes duplicates and ensures data consistency."""
    if df.empty:
        logging.warning("⚠️ No data retrieved!")
        return df
    df.drop_duplicates(
        subset=["id"], inplace=True
    ) if "id" in df.columns else df.drop_duplicates(inplace=True)
    return df


def get_dpe_data(
    start_date, end_date, size, api_url, batch_days, query_field, query_geo
):
    """Runs the async data fetching function synchronously."""

    async def run_query():
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit_per_host=5)
        ) as session:
            return await query_dpe_data_df(
                session,
                start_date,
                end_date,
                size,
                api_url,
                batch_days,
                query_field,
                query_geo,
            )

    return asyncio.run(run_query())


def generate_date_intervals(start_date, end_date, interval_days=10):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    date_intervals = []
    current_start = start_date

    while current_start <= end_date:
        current_end = current_start + timedelta(days=interval_days - 1)
        if current_end > end_date:
            current_end = end_date
        date_intervals.append(
            (current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d"))
        )
        current_start = current_end + timedelta(days=1)

    return date_intervals


async def insert_into_db(
    df: pd.DataFrame,
    db_config: dict = DEFAULT_DB_CONFIG,
    schema_name: str = "ademe",
    table_name: str = "ademe_new",
    id_column: str = "N°DPE",  # Unique ID
    index_column: str = "ademe_address",  # Column used for merging
):
    """Efficiently insert DataFrame into PostgreSQL, ensuring correct indexing and optimized retrieval."""

    if df.empty:
        logging.warning("⚠️ No data to insert into the database.")
        return

    # Ensure required columns exist
    required_columns = {id_column, index_column}
    if not required_columns.issubset(set(df.columns)):
        raise ValueError(
            f"❌ DataFrame must contain required columns: {required_columns}"
        )

    # Handle NaN values by replacing them with `null` in JSON (valid for JSONB)
    df = df.copy()  # Avoid modifying the original DataFrame

    # Convert all other fields into a JSONB column and handle NaNs
    json_columns = [col for col in df.columns if col not in required_columns]
    df["other_columns"] = df[json_columns].apply(
        lambda row: json.dumps(
            {
                k: (v if not pd.isna(v) else None)  # Replace NaN with None (valid JSON)
                for k, v in row.to_dict().items()
            }
        ),
        axis=1,
    )

    # Keep only ID, indexing column, and the newly created JSONB column
    df = df[[id_column, index_column, "other_columns"]]

    # Convert DataFrame to list of tuples for asyncpg
    records = list(df.itertuples(index=False, name=None))

    # Start timing the insertion process
    start_time = time.time()

    async with asyncpg.create_pool(**db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Ensure schema exists
                await conn.execute(
                    f"""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = '{schema_name}') THEN
                            EXECUTE 'CREATE SCHEMA {schema_name}';
                        END IF;
                    END $$;
                    """
                )

                # Ensure table exists
                await conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
                        {id_column} TEXT PRIMARY KEY,
                        {index_column} TEXT,
                        other_columns JSONB
                    );

                    CREATE INDEX IF NOT EXISTS {table_name}_ademe_address_idx
                    ON {schema_name}.{table_name} ({index_column});
                    """
                )

                # Insert or update records
                insert_query = f"""
                    INSERT INTO {schema_name}.{table_name} ({id_column}, {index_column}, other_columns)
                    VALUES ($1, $2, $3)
                    ON CONFLICT ({id_column}) DO UPDATE
                    SET {index_column} = EXCLUDED.{index_column},
                        other_columns = EXCLUDED.other_columns;
                """

                # Execute batch insert
                await conn.executemany(insert_query, records)

    # End timing the insertion process
    end_time = time.time()

    # Calculate and log how long the insertion took
    insertion_time = end_time - start_time
    logging.info(
        f"✅ Data successfully inserted into {schema_name}.{table_name} with indexed `{index_column}`."
    )
    logging.info(f"⏱️ Insertion took {insertion_time:.2f} seconds.")
    logging.info("🚀 Insert operation completed!")


async def master_fetching_async(
    start_date: str,
    end_date: str,
    api_url: str,
    query_field: str,
    query_geo: int,
    db_config: dict = None,
):
    """Fetches data in batches and merges into a master DataFrame asynchronously."""

    # Use the default DB config if none is provided
    if db_config is None:
        db_config = DEFAULT_DB_CONFIG

    master = pd.DataFrame()
    date_intervals = generate_date_intervals(start_date, end_date)

    async with asyncio.Semaphore(2):  # Limit concurrent requests
        for date in date_intervals:
            loggers = f"📅 Fetching data for {date} intervals."
            if query_geo:
                loggers += f" covering subregion: {query_geo}"
            logging.info(loggers)

            df = await get_dpe_data_async(
                date[0],
                date[1],
                size=10000,
                api_url=api_url,
                batch_days=1,
                query_field=query_field,
                query_geo=query_geo,
            )

            if not df.empty:
                master = pd.concat([master, df], ignore_index=True)
                logging.info(
                    f"✅ Retrieved {df.shape[0]} records from {date[0]} to {date[1]}.\n"
                )
            else:
                logging.warning(f"⚠️ No data retrieved for {date[0]} to {date[1]}.\n")

    # Deduplication
    master.drop_duplicates(inplace=True)

    # Build address field (only if master is not empty)
    if len(master) > 0:
        if "numero_voie_ban" in sorted(master.columns):
            master["ademe_address"] = master["adresse_ban"].astype(str)
        elif "adresse_ban" in master.columns:
            master["ademe_address"] = master["adresse_ban"].astype(str)
        elif "geo_adresse" in master.columns:
            master["ademe_address"] = master.geo_adresse.astype(str)
        else:
            logging.error("❌ No address column found in data!")
    else:
        logging.warning("⚠️ Empty dataset, skipping address field creation")

    # Insert data into PostgreSQL
    # await insert_into_db(master, db_config)

    logging.info(
        f"🎯 Final dataset size after deduplication: {master.shape[0]} records."
    )

    # Export data to GCS (only if not empty)
    if len(master) > 0:
        export_to_gcs(
            bucket_name="ma-data-dev",
            blob_name=f"ADEME/RAW/ADEME_RAW_SUBREGION_CODE_{query_geo}",
            new_df=master,
        )
    else:
        logging.warning("⚠️ Skipping GCS export for empty dataset")

    return master


def master_fetching(
    start_date: str, end_date: str, api_url: str, query_field: str, query_geo: int
):
    """Runs the async master_fetching function synchronously."""
    return asyncio.run(
        master_fetching_async(start_date, end_date, api_url, query_field, query_geo)
    )


async def get_dpe_data_async(
    start_date, end_date, size, api_url, batch_days, query_field, query_geo
):
    """Async wrapper for fetching DPE data."""
    async with aiohttp.ClientSession() as session:
        return await query_dpe_data_df(
            session,
            start_date,
            end_date,
            size,
            api_url,
            batch_days,
            query_field,
            query_geo,
        )
