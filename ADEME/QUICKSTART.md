# ADEME Bulk Fetch - Quick Start Guide

## Step-by-Step Setup

### 1. Install Missing Dependencies (if needed)

```bash
cd /Users/bpatras/dpe_migration/science_project/core/ADEME
pip install unidecode asyncpg
```

### 2. Update Database Password

Edit `bulk_fetch.py` line 33-39 and replace `****` with your actual database password:

```python
DEFAULT_DB_CONFIG = {
    "user": "customdb",
    "password": "YOUR_ACTUAL_PASSWORD_HERE",  # Replace ****
    "database": "listing_dev",
    "host": "localhost",
    "port": 1111,
}
```

### 3. Run Quick Test (No Database Required)

This tests your Python environment and dependencies:

```bash
python quick_test.py
```

Expected output: All 5 tests should pass ✅

### 4. Run Full Test (Requires Database Connection)

This tests database connection and existing data:

```bash
python test_bulk_fetch.py
```

If database is not set up yet, it will show setup instructions.

### 5. One-Time Database Setup (15-30 minutes)

Import the full ADEME database:

```bash
python setup_bulk_fetch.py --setup
```

This downloads ~3GB of data and imports it to PostgreSQL.

**OR** do it in Python:

```python
from bulk_fetch import ADEMEBulkLoader

loader = ADEMEBulkLoader()
loader.download_and_import_dump()  # Takes 15-30 minutes
```

### 6. Verify Setup

Check database statistics:

```bash
python setup_bulk_fetch.py --stats
```

Should show ~13-14 million records.

### 7. Test Performance

Run a quick benchmark:

```bash
python benchmark_comparison.py
```

Should show queries completing in 2-5 seconds.

### 8. Use in Your Code

Replace existing `geocode.run_geocoding()` calls:

```python
from geocode_optimized import run_geocoding_optimized

# Old way (30-60 minutes per department)
# from geocode import run_geocoding
# data, failed = run_geocoding(...)

# New way (2-5 seconds per department)
data, failed = run_geocoding_optimized(
    start_date="2024-01-01",
    end_date="2024-12-31",
    query_geo=75  # Paris
)
```

## Troubleshooting

### "psql: command not found"

Install PostgreSQL client tools:

```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql-client
```

### "Connection refused"

1. Check if PostgreSQL is running
2. Verify SSH tunnel if connecting to remote database
3. Check port 1111 is correct

### "Permission denied"

Grant schema creation permission:

```sql
GRANT CREATE ON DATABASE listing_dev TO customdb;
```

### Missing packages

Install all required packages:

```bash
pip install pandas psycopg2-binary requests aiohttp google-cloud-storage numpy unidecode asyncpg
```

## Weekly Maintenance

Update database with recent data (takes ~1-2 minutes):

```bash
python setup_bulk_fetch.py --update
```

Or in Python:

```python
from bulk_fetch import ADEMEBulkLoader

loader = ADEMEBulkLoader()
loader.update_recent_data(days_back=7)
```

## Quick Reference

| Command                               | Purpose                         |
| ------------------------------------- | ------------------------------- |
| `python quick_test.py`                | Test environment (no DB needed) |
| `python test_bulk_fetch.py`           | Full test suite                 |
| `python setup_bulk_fetch.py --setup`  | One-time database import        |
| `python setup_bulk_fetch.py --stats`  | Show database statistics        |
| `python setup_bulk_fetch.py --test`   | Performance test                |
| `python setup_bulk_fetch.py --update` | Weekly data refresh             |
| `python benchmark_comparison.py`      | Compare old vs new speed        |

## Support

See `BULK_FETCH_README.md` for detailed documentation.
