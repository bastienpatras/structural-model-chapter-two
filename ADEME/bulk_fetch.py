"""
Optimized ADEME DPE data fetching module using bulk download and local database storage.

This module provides an efficient alternative to paginated API calls by:
1. Downloading the complete PostgreSQL dump from ADEME
2. Importing to local PostgreSQL database
3. Querying locally with full SQL capabilities
4. Supporting incremental updates for new data

Usage:
    from bulk_fetch import ADEMEBulkLoader

    # One-time setup
    loader = ADEMEBulkLoader()
    loader.download_and_import_dump()

    # Query data locally
    df = loader.get_dpe_data(query_geo=75, start_date="2024-01-01", end_date="2024-12-31")

    # Incremental update (weekly)
    loader.update_recent_data(days_back=7)
"""

import gzip
import logging
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import psycopg2
import requests
from psycopg2 import sql
from tools import export_to_gcs


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Database configuration for local testing
# Adjust these for your setup
DEFAULT_DB_CONFIG = {
    "user": "customdb",  # Your macOS username
    "password": "****",  # No password for local testing
    "database": "listing_dev",  # ADEME database
    "host": "localhost",
    "port": 1111,  # Standard PostgreSQL port
}

# ADEME API configuration
DUMP_URL = "https://opendata.ademe.fr/dump_dpev2_prod_fdld.sql.gz"
API_URL = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines"
SCHEMA_NAME = "ademe"
TABLE_NAME = "dpe"


class ADEMEBulkLoader:
    """
    Handles bulk loading and querying of ADEME DPE data.

    Provides methods to download the full PostgreSQL dump, import it to a local database,
    and query the data efficiently without API rate limits.
    """

    def __init__(self, db_config: dict = None):
        """
        Initialize the bulk loader with database configuration.

        Args:
            db_config: PostgreSQL connection config. Uses DEFAULT_DB_CONFIG if None.
        """
        self.db_config = db_config or DEFAULT_DB_CONFIG
        self.schema = SCHEMA_NAME
        self.table = TABLE_NAME

    def get_connection(self):
        """Create and return a database connection."""
        return psycopg2.connect(**self.db_config)

    def download_dump(self, output_path: Path = None) -> Path:
        """
        Download the ADEME PostgreSQL dump file with robust error handling.

        Args:
            output_path: Where to save the dump. Uses temp file if None.

        Returns:
            Path to the downloaded dump file.
        """
        if output_path is None:
            output_path = Path(tempfile.gettempdir()) / "ademe_dpe_dump.sql.gz"

        logger.info("📥 Downloading ADEME dump from {DUMP_URL}")
        logger.info("This may take several minutes (file is ~6-7 GB)...")

        # Use longer timeout for large files
        timeout = (30, 300)  # (connect timeout, read timeout)

        try:
            response = requests.get(DUMP_URL, stream=True, timeout=timeout)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            last_log_mb = 0

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):  # 1MB chunks
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        f.flush()  # Ensure data is written to disk
                        downloaded += len(chunk)

                        # Log every 100MB
                        current_mb = downloaded // (100 * 1024 * 1024)
                        if current_mb > last_log_mb:
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                logger.info(
                                    f"   Progress: {progress:.1f}% ({downloaded / (1024**3):.2f} GB / {total_size / (1024**3):.2f} GB)"
                                )
                            else:
                                logger.info(
                                    f"   Downloaded: {downloaded / (1024**3):.2f} GB"
                                )
                            last_log_mb = current_mb

            # Verify download completed
            actual_size = output_path.stat().st_size
            if total_size > 0 and actual_size != total_size:
                raise Exception(
                    f"Download incomplete: expected {total_size} bytes, got {actual_size}"
                )

            logger.info(
                f"✅ Download complete: {output_path} ({actual_size / (1024**3):.2f} GB)"
            )

            # Verify it's a valid gzip file
            logger.info("🔍 Verifying file integrity...")
            import subprocess

            result = subprocess.run(
                ["gunzip", "-t", str(output_path)], capture_output=True, timeout=60
            )
            if result.returncode != 0:
                raise Exception(
                    f"Downloaded file is corrupted: {result.stderr.decode()}"
                )

            logger.info("✅ File integrity verified")
            return output_path

        except requests.exceptions.Timeout:
            logger.error(
                "❌ Download timeout - file may be too large or connection too slow"
            )
            raise
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            # Clean up partial download
            if output_path.exists():
                output_path.unlink()
            raise

    def create_schema_and_table(self):
        """
        Create the ademe schema if it doesn't exist.
        The table will be created by the SQL dump import.
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # Create schema
                cursor.execute(
                    sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                        sql.Identifier(self.schema)
                    )
                )
                conn.commit()
                logger.info(f"✅ Schema '{self.schema}' ready")
        finally:
            conn.close()

    def import_dump(self, dump_path: Path):
        """
        Import the PostgreSQL dump into the local database.

        Args:
            dump_path: Path to the .sql.gz dump file.
        """
        logger.info("📦 Decompressing and importing dump...")
        logger.info("   This will take 10-30 minutes depending on your system...")

        # Decompress to temporary SQL file
        sql_path = dump_path.with_suffix("")  # Remove .gz extension

        with gzip.open(dump_path, "rb") as f_in:
            with open(sql_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        logger.info(f"✅ Decompression complete: {sql_path}")

        # Modify SQL to import into our schema
        logger.info(f"📝 Adapting SQL for schema '{self.schema}'...")
        adapted_sql = self._adapt_sql_for_schema(sql_path)

        # Import using psql command line tool
        logger.info("🔄 Importing to PostgreSQL...")

        env = {"PGPASSWORD": self.db_config["password"]}

        cmd = [
            "psql",
            "-h",
            str(self.db_config["host"]),
            "-U",
            self.db_config["user"],
            "-d",
            self.db_config["database"],
            "-p",
            str(self.db_config["port"]),
            "-f",
            str(adapted_sql),
            "-v",
            "ON_ERROR_STOP=1",
        ]

        try:
            result = subprocess.run(
                cmd, env=env, capture_output=True, text=True, check=True
            )
            logger.info("✅ Import successful")
            if result.stdout:
                logger.debug(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Import failed: {e.stderr}")
            raise
        finally:
            # Cleanup temporary files
            sql_path.unlink(missing_ok=True)
            adapted_sql.unlink(missing_ok=True)

    def _adapt_sql_for_schema(self, sql_path: Path) -> Path:
        """
        Adapt the SQL dump to use our custom schema.

        Args:
            sql_path: Path to the original SQL file.

        Returns:
            Path to the adapted SQL file.
        """
        adapted_path = sql_path.with_suffix(".adapted.sql")

        with open(sql_path, "r", encoding="utf-8", errors="ignore") as f_in:
            with open(adapted_path, "w", encoding="utf-8") as f_out:
                # Add schema prefix
                f_out.write(f"SET search_path TO {self.schema}, public;\n\n")

                for line in f_in:
                    # Skip commands that might conflict
                    if any(
                        skip in line.upper()
                        for skip in ["CREATE DATABASE", "DROP DATABASE"]
                    ):
                        continue
                    f_out.write(line)

        return adapted_path

    def create_indexes(self):
        """
        Create optimized indexes for common query patterns.
        """
        logger.info("📊 Creating indexes for optimized queries...")

        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                indexes = [
                    # Index for department + date filtering
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_{self.table}_dept_date
                    ON {self.schema}.{self.table} (code_departement_ban, date_reception_dpe)
                    """,
                    # Index for address matching
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_{self.table}_address
                    ON {self.schema}.{self.table} (adresse_ban)
                    """,
                    # Index for DPE number lookups
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_{self.table}_numero
                    ON {self.schema}.{self.table} (numero_dpe)
                    """,
                    # Index for active DPEs only
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_{self.table}_active
                    ON {self.schema}.{self.table} (dpe_desactive)
                    WHERE dpe_desactive = 0
                    """,
                ]

                for index_sql in indexes:
                    cursor.execute(index_sql)
                    conn.commit()

                logger.info("✅ Indexes created successfully")
        finally:
            conn.close()

    def download_and_import_dump(self):
        """
        Complete workflow: download dump, import, and create indexes.
        This is a one-time setup operation.
        """
        logger.info("🚀 Starting bulk import workflow...")

        # Step 1: Create schema
        self.create_schema_and_table()

        # Step 2: Download dump
        dump_path = self.download_dump()

        # Step 3: Import dump
        try:
            self.import_dump(dump_path)
        finally:
            # Cleanup dump file
            dump_path.unlink(missing_ok=True)
            logger.info("🧹 Cleaned up temporary files")

        # Step 4: Create indexes
        self.create_indexes()

        logger.info("🎉 Bulk import complete! Database is ready for queries.")

    def get_dpe_data(
        self,
        query_geo: int = None,
        start_date: str = None,
        end_date: str = None,
        limit: int = None,
        active_only: bool = True,
        chunksize: int = None,
    ) -> pd.DataFrame:
        """
        Query DPE data from local database with memory optimization.

        Args:
            query_geo: Department code (code_departement_ban).
            start_date: Start date (YYYY-MM-DD format).
            end_date: End date (YYYY-MM-DD format).
            limit: Maximum number of records to return.
            active_only: Only return active DPEs (dpe_desactive = 0).
            chunksize: If set, returns iterator instead of DataFrame (memory efficient).

        Returns:
            DataFrame with DPE records, or iterator if chunksize is set.
        """
        conditions = []
        params = {}

        if active_only:
            conditions.append("dpe_desactive = 0")

        if query_geo is not None:
            conditions.append("code_departement_ban = %(dept)s")
            params["dept"] = str(query_geo)

        if start_date:
            conditions.append("date_reception_dpe >= %(start_date)s")
            params["start_date"] = start_date

        if end_date:
            conditions.append("date_reception_dpe <= %(end_date)s")
            params["end_date"] = end_date

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        limit_clause = f"LIMIT {limit}" if limit else ""

        query = f"""
            SELECT *
            FROM {self.schema}.{self.table}
            WHERE {where_clause}
            ORDER BY date_reception_dpe DESC
            {limit_clause}
        """

        logger.info("📊 Querying local database...")
        logger.info(f"   Filters: dept={query_geo}, dates={start_date} to {end_date}")
        if chunksize:
            logger.info(
                f"   ⚡ Using chunked reading (chunksize={chunksize}) for memory efficiency"
            )

        conn = self.get_connection()
        try:
            # Memory-efficient chunked reading
            if chunksize:
                return pd.read_sql(query, conn, params=params, chunksize=chunksize)
            else:
                df = pd.read_sql(query, conn, params=params)
                logger.info(f"✅ Retrieved {len(df)} records")
                # Estimate memory usage
                memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
                logger.info(f"   Memory used: ~{memory_mb:.1f} MB")
                return df
        finally:
            if not chunksize:  # Don't close if returning iterator
                conn.close()

    def update_recent_data(self, days_back: int = 7):
        """
        Update the database with recent data from the API.
        Use this for incremental weekly updates.

        Args:
            days_back: How many days back to fetch from the API.
        """
        from fetch import get_dpe_data  # Import existing API fetcher

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        logger.info(f"🔄 Fetching updates from API for last {days_back} days...")

        # Use existing API fetcher for recent data
        df = get_dpe_data(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            size=10000,
            api_url=API_URL,
            batch_days=1,
            query_field="date_reception_dpe",
            query_geo=None,  # Fetch all departments
        )

        if df.empty:
            logger.info("ℹ️ No new records to update")
            return

        # Insert/update records in database
        logger.info(f"💾 Upserting {len(df)} records to database...")
        self._upsert_dataframe(df)

        logger.info(f"✅ Database updated with {len(df)} new/updated records")

    def _upsert_dataframe(self, df: pd.DataFrame):
        """
        Insert or update records in the database.

        Args:
            df: DataFrame with DPE records to upsert.
        """
        if df.empty:
            return

        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # Create temporary table
                cursor.execute(
                    f"""
                    CREATE TEMP TABLE temp_dpe (LIKE {self.schema}.{self.table})
                """
                )

                # Copy data to temp table
                from io import StringIO

                buffer = StringIO()
                df.to_csv(buffer, index=False, header=False)
                buffer.seek(0)

                cursor.copy_from(
                    buffer, "temp_dpe", sep=",", null="", columns=df.columns.tolist()
                )

                # Upsert from temp to main table
                cursor.execute(
                    f"""
                    INSERT INTO {self.schema}.{self.table}
                    SELECT * FROM temp_dpe
                    ON CONFLICT (numero_dpe)
                    DO UPDATE SET
                        date_reception_dpe = EXCLUDED.date_reception_dpe,
                        adresse_ban = EXCLUDED.adresse_ban
                        -- Add other columns as needed
                """
                )

                conn.commit()
        finally:
            conn.close()

    def get_database_stats(self) -> dict:
        """
        Get statistics about the local DPE database.

        Returns:
            Dictionary with database statistics.
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # Total records
                cursor.execute(f"SELECT COUNT(*) FROM {self.schema}.{self.table}")
                total_count = cursor.fetchone()[0]

                # Active records
                cursor.execute(
                    f"""
                    SELECT COUNT(*) FROM {self.schema}.{self.table}
                    WHERE dpe_desactive = 0
                """
                )
                active_count = cursor.fetchone()[0]

                # Date range
                cursor.execute(
                    f"""
                    SELECT
                        MIN(date_reception_dpe) as min_date,
                        MAX(date_reception_dpe) as max_date
                    FROM {self.schema}.{self.table}
                """
                )
                min_date, max_date = cursor.fetchone()

                # Department coverage
                cursor.execute(
                    f"""
                    SELECT COUNT(DISTINCT code_departement_ban)
                    FROM {self.schema}.{self.table}
                """
                )
                dept_count = cursor.fetchone()[0]

                stats = {
                    "total_records": total_count,
                    "active_records": active_count,
                    "inactive_records": total_count - active_count,
                    "date_range": {"min": min_date, "max": max_date},
                    "departments": dept_count,
                }

                logger.info("📊 Database Statistics:")
                logger.info(f"   Total records: {total_count:,}")
                logger.info(f"   Active records: {active_count:,}")
                logger.info(f"   Date range: {min_date} to {max_date}")
                logger.info(f"   Departments: {dept_count}")

                return stats
        finally:
            conn.close()

    def export_to_gcs_by_department(self, bucket_name: str = "ma-data-dev"):
        """
        Export data to GCS, organized by department.
        Maintains compatibility with existing pipeline.

        Args:
            bucket_name: GCS bucket name.
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # Get list of departments
                cursor.execute(
                    f"""
                    SELECT DISTINCT code_departement_ban
                    FROM {self.schema}.{self.table}
                    WHERE code_departement_ban IS NOT NULL
                    ORDER BY code_departement_ban
                """
                )
                departments = [row[0] for row in cursor.fetchall()]

                logger.info(f"📤 Exporting {len(departments)} departments to GCS...")

                for dept in departments:
                    df = self.get_dpe_data(query_geo=int(dept))

                    if not df.empty:
                        export_to_gcs(
                            bucket_name=bucket_name,
                            blob_name=f"ADEME/RAW/ADEME_RAW_SUBREGION_CODE_{dept}",
                            new_df=df,
                        )
                        logger.info(f"✅ Exported department {dept}: {len(df)} records")
        finally:
            conn.close()


# Convenience functions for backward compatibility


def get_dpe_data_local(
    query_geo: int, start_date: str = None, end_date: str = None, db_config: dict = None
) -> pd.DataFrame:
    """
    Backward-compatible function to get DPE data from local database.

    Args:
        query_geo: Department code.
        start_date: Start date (YYYY-MM-DD).
        end_date: End date (YYYY-MM-DD).
        db_config: Database configuration.

    Returns:
        DataFrame with DPE records.
    """
    loader = ADEMEBulkLoader(db_config)
    return loader.get_dpe_data(
        query_geo=query_geo, start_date=start_date, end_date=end_date
    )


if __name__ == "__main__":
    # Example usage
    loader = ADEMEBulkLoader()

    # One-time setup (uncomment to run)
    # loader.download_and_import_dump()

    # Get statistics
    loader.get_database_stats()

    # Query example: Paris (75) data from 2024
    df = loader.get_dpe_data(
        query_geo=75, start_date="2024-01-01", end_date="2024-12-31"
    )
    print(f"\n📊 Sample data:\n{df.head()}")
