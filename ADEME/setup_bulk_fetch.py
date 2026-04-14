#!/usr/bin/env python3
"""
Setup script for ADEME bulk fetch module.

This script helps you set up the local database for faster ADEME data queries.

Usage:
    python setup_bulk_fetch.py --setup      # One-time database setup
    python setup_bulk_fetch.py --stats      # Show database statistics
    python setup_bulk_fetch.py --update     # Update with recent data
    python setup_bulk_fetch.py --test       # Test query performance
"""

import argparse
import sys
import time
from datetime import datetime, timedelta

from bulk_fetch import ADEMEBulkLoader


def setup_database():
    """Run the complete database setup."""
    print("🚀 Starting ADEME Database Setup")
    print("=" * 60)
    print()
    print("This will:")
    print("  1. Download ~2-3 GB of data from ADEME")
    print("  2. Import to PostgreSQL (takes 15-30 minutes)")
    print("  3. Create optimized indexes")
    print()
    response = input("Continue? [y/N]: ")

    if response.lower() != "y":
        print("Setup cancelled.")
        return

    try:
        loader = ADEMEBulkLoader()

        print("\n📊 Checking if database already exists...")
        try:
            stats = loader.get_database_stats()
            print(
                f"⚠️  Database already exists with {stats['total_records']:,} records"
            )
            response = input("Re-import? This will DROP existing data. [y/N]: ")

            if response.lower() != "y":
                print("Setup cancelled.")
                return
        except Exception:
            print("✓ Database not found, proceeding with import")

        print("\n🔧 Starting import process...")
        start_time = time.time()

        loader.download_and_import_dump()

        elapsed = time.time() - start_time
        print(f"\n✅ Setup complete in {elapsed/60:.1f} minutes!")

        # Show stats
        stats = loader.get_database_stats()

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


def show_stats():
    """Display database statistics."""
    try:
        loader = ADEMEBulkLoader()
        stats = loader.get_database_stats()

        print("\n" + "=" * 60)
        print("ADEME DATABASE STATISTICS")
        print("=" * 60)
        print()
        print(f"📊 Total Records:     {stats['total_records']:,}")
        print(f"✅ Active Records:    {stats['active_records']:,}")
        print(f"❌ Inactive Records:  {stats['inactive_records']:,}")
        print(
            f"📅 Date Range:        {stats['date_range']['min']} to {stats['date_range']['max']}"
        )
        print(f"🗺️  Departments:       {stats['departments']}")
        print()

    except Exception as e:
        print(f"❌ Failed to get statistics: {e}")
        print("\nHave you run --setup yet?")
        sys.exit(1)


def update_database(days: int = 7):
    """Update database with recent data."""
    print(f"🔄 Updating database with last {days} days of data...")

    try:
        loader = ADEMEBulkLoader()
        loader.update_recent_data(days_back=days)
        print("✅ Update complete!")

    except Exception as e:
        print(f"❌ Update failed: {e}")
        sys.exit(1)


def run_performance_test():
    """Test query performance."""
    print("🏃 Running Performance Test")
    print("=" * 60)

    try:
        loader = ADEMEBulkLoader()

        # Test 1: Single department, full year
        print("\nTest 1: Paris (75) - Full year 2024")
        start = time.time()
        df1 = loader.get_dpe_data(
            query_geo=75, start_date="2024-01-01", end_date="2024-12-31"
        )
        elapsed1 = time.time() - start
        print(f"  ✓ Retrieved {len(df1):,} records in {elapsed1:.2f} seconds")

        # Test 2: Single department, single month
        print("\nTest 2: Paris (75) - January 2024")
        start = time.time()
        df2 = loader.get_dpe_data(
            query_geo=75, start_date="2024-01-01", end_date="2024-01-31"
        )
        elapsed2 = time.time() - start
        print(f"  ✓ Retrieved {len(df2):,} records in {elapsed2:.2f} seconds")

        # Test 3: No filters (should be slower)
        print("\nTest 3: All departments - Last 7 days")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        start = time.time()
        df3 = loader.get_dpe_data(start_date=week_ago, end_date=today)
        elapsed3 = time.time() - start
        print(f"  ✓ Retrieved {len(df3):,} records in {elapsed3:.2f} seconds")

        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"Average query time: {(elapsed1 + elapsed2 + elapsed3) / 3:.2f} seconds")
        print(f"Total records retrieved: {len(df1) + len(df2) + len(df3):,}")
        print()
        print("💡 Tip: Filtering by department makes queries ~10x faster!")

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        print("\nHave you run --setup yet?")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Setup and manage ADEME bulk fetch database"
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run one-time database setup (downloads and imports full dataset)",
    )

    parser.add_argument("--stats", action="store_true", help="Show database statistics")

    parser.add_argument(
        "--update",
        action="store_true",
        help="Update database with recent data from API",
    )

    parser.add_argument(
        "--update-days",
        type=int,
        default=7,
        help="Number of days to fetch for update (default: 7)",
    )

    parser.add_argument(
        "--test", action="store_true", help="Run performance test queries"
    )

    args = parser.parse_args()

    # If no arguments provided, show help
    if not any([args.setup, args.stats, args.update, args.test]):
        parser.print_help()
        return

    # Execute requested actions
    if args.setup:
        setup_database()

    if args.stats:
        show_stats()

    if args.update:
        update_database(days=args.update_days)

    if args.test:
        run_performance_test()


if __name__ == "__main__":
    main()
