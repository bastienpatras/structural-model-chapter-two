#!/usr/bin/env python3
"""
Quick test - verify Python environment without database.

This test runs immediately without requiring database setup.
Use this first to check if all dependencies are installed.

Usage:
    python quick_test.py
"""

import sys


def test_python_version():
    """Check Python version."""
    print("🐍 Python Version Check")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Python version OK (3.8+)")
        return True
    else:
        print("   ❌ Python 3.8+ required")
        return False


def test_required_packages():
    """Check if required packages are installed."""
    print("\n📦 Required Packages Check")

    required = {
        "pandas": "pandas",
        "psycopg2": "psycopg2-binary",
        "requests": "requests",
        "aiohttp": "aiohttp",
        "google.cloud.storage": "google-cloud-storage",
        "numpy": "numpy",
        "unidecode": "unidecode",
        "asyncpg": "asyncpg",
    }

    missing = []
    installed = []

    for module, package in required.items():
        try:
            __import__(module)
            installed.append(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"   ❌ {package} - NOT INSTALLED")

    if missing:
        print(f"\n❌ Missing {len(missing)} packages")
        print("\nInstall with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    else:
        print(f"\n✅ All {len(installed)} required packages installed")
        return True


def test_module_imports():
    """Test importing the custom modules."""
    print("\n📁 Custom Modules Check")

    modules = [
        ("bulk_fetch", "ADEMEBulkLoader"),
        ("geocode_optimized", "run_geocoding_optimized"),
        ("tools", "export_to_gcs"),
        ("tagging", "fast_extract_info"),
    ]

    all_ok = True

    for module_name, class_or_func in modules:
        try:
            module = __import__(module_name)
            obj = getattr(module, class_or_func, None)
            if obj:
                print(f"   ✅ {module_name}.{class_or_func}")
            else:
                print(f"   ⚠️  {module_name} imported but {class_or_func} not found")
                all_ok = False
        except ImportError as e:
            print(f"   ❌ {module_name} - {e}")
            all_ok = False
        except Exception as e:
            print(f"   ⚠️  {module_name} - {e}")
            all_ok = False

    return all_ok


def test_database_config():
    """Test database configuration (without connecting)."""
    print("\n🔧 Database Configuration Check")

    try:
        from bulk_fetch import DEFAULT_DB_CONFIG

        print("   Configuration found:")
        print(f"     • Host: {DEFAULT_DB_CONFIG['host']}")
        print(f"     • Port: {DEFAULT_DB_CONFIG['port']}")
        print(f"     • Database: {DEFAULT_DB_CONFIG['database']}")
        print(f"     • User: {DEFAULT_DB_CONFIG['user']}")
        print(f"     • Password: {'*' * len(DEFAULT_DB_CONFIG['password'])}")

        if DEFAULT_DB_CONFIG["password"] == "****":
            print("\n   ⚠️  Default password detected")
            print(
                "   Update DEFAULT_DB_CONFIG in bulk_fetch.py with your actual password"
            )
            return False
        else:
            print("\n   ✅ Configuration looks good")
            return True

    except Exception as e:
        print(f"   ❌ Error reading config: {e}")
        return False


def test_file_structure():
    """Check if all required files exist."""
    print("\n📄 File Structure Check")

    from pathlib import Path

    base_dir = Path(__file__).parent
    required_files = [
        "bulk_fetch.py",
        "geocode_optimized.py",
        "setup_bulk_fetch.py",
        "benchmark_comparison.py",
        "test_bulk_fetch.py",
        "BULK_FETCH_README.md",
        "tools.py",
        "tagging.py",
    ]

    all_exist = True
    for filename in required_files:
        filepath = base_dir / filename
        if filepath.exists():
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} - NOT FOUND")
            all_exist = False

    return all_exist


def main():
    """Run all quick tests."""
    print("\n" + "=" * 70)
    print("  QUICK ENVIRONMENT TEST")
    print("  (No database connection required)")
    print("=" * 70)

    results = {
        "Python Version": test_python_version(),
        "Required Packages": test_required_packages(),
        "File Structure": test_file_structure(),
        "Database Config": test_database_config(),
        "Module Imports": test_module_imports(),
    }

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")
    print()

    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")

    print()

    if passed == total:
        print("🎉 Environment ready!")
        print("\nNext steps:")
        print("  1. Run full test: python test_bulk_fetch.py")
        print("  2. Setup database: python setup_bulk_fetch.py --setup")
    else:
        print("⚠️  Fix the issues above before proceeding")

    print()

    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
