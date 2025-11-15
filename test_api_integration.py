#!/usr/bin/env python3
"""Test script to verify Notion API integration with latest API version."""

import os
import sys
import requests
from notion_client import Client

# Load environment variables
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_API_VERSION = os.getenv("NOTION_API_VERSION", "2025-09-03")
API_BASE_URL = "http://localhost:8000"

if not NOTION_API_KEY:
    print("ERROR: NOTION_API_KEY environment variable is not set")
    print("Please set it in your .env file or export it before running this script")
    exit(1)


def test_notion_client():
    """Test direct Notion API connection."""
    print(f"\n{'='*60}")
    print("Testing Notion API Client")
    print(f"{'='*60}")
    print(f"API Version: {NOTION_API_VERSION}")

    try:
        notion = Client(
            auth=NOTION_API_KEY,
            notion_version=NOTION_API_VERSION
        )

        # Test: List users
        print("\n[TEST] Listing Notion users...")
        users = notion.users.list()
        print(f"✓ Successfully connected to Notion API v{NOTION_API_VERSION}")
        print(f"  Found {len(users.get('results', []))} users")

        # Test: Search for databases (data_source in new API)
        print("\n[TEST] Searching for databases...")
        search_result = notion.search(filter={"property": "object", "value": "data_source"})
        databases = search_result.get("results", [])
        print(f"✓ Found {len(databases)} accessible database(s)")

        if databases:
            print("\n  Available Databases:")
            for db in databases[:3]:  # Show first 3
                db_id = db.get("id", "N/A")
                db_title = ""
                if "title" in db:
                    title_parts = db["title"]
                    if title_parts:
                        db_title = title_parts[0].get("plain_text", "Untitled")
                print(f"    - {db_title or 'Untitled'} (ID: {db_id})")

        return True

    except Exception as e:
        print(f"✗ Error connecting to Notion API: {e}")
        return False


def test_api_health():
    """Test API health endpoint."""
    print(f"\n{'='*60}")
    print("Testing API Health")
    print(f"{'='*60}")

    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        data = response.json()

        print(f"✓ API Status: {data.get('status')}")

        # Check database health
        db_status = data.get("checks", {}).get("database", {})
        print(f"  Database: {db_status.get('status')}")

        # Check Notion API health
        notion_status = data.get("checks", {}).get("notion", {})
        print(f"  Notion API: {notion_status.get('status')}")
        api_version = notion_status.get("notion_api", {}).get("api_version")
        print(f"  API Version: {api_version}")

        if api_version == NOTION_API_VERSION:
            print(f"✓ Using latest Notion API version: {api_version}")
            return True
        else:
            print(f"✗ API version mismatch. Expected: {NOTION_API_VERSION}, Got: {api_version}")
            return False

    except Exception as e:
        print(f"✗ Error checking API health: {e}")
        return False


def test_api_endpoints():
    """Test various API endpoints."""
    print(f"\n{'='*60}")
    print("Testing API Endpoints")
    print(f"{'='*60}")

    tests_passed = 0
    tests_total = 0

    # Test 1: Root endpoint
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE_URL}/")
        response.raise_for_status()
        data = response.json()
        print(f"✓ Root endpoint: {data.get('name')}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")

    # Test 2: Docs endpoint
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        if response.status_code == 200:
            print(f"✓ API docs accessible at {API_BASE_URL}/docs")
            tests_passed += 1
        else:
            print(f"✗ API docs not accessible")
    except Exception as e:
        print(f"✗ Docs endpoint failed: {e}")

    # Test 3: User mappings list
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE_URL}/users/mappings/")
        response.raise_for_status()
        data = response.json()
        print(f"✓ User mappings endpoint: {data.get('total', 0)} mappings")
        tests_passed += 1
    except Exception as e:
        print(f"✗ User mappings endpoint failed: {e}")

    print(f"\nEndpoint Tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("NOTION BOT API INTEGRATION TEST")
    print("="*60)

    all_passed = True

    # Run tests
    all_passed &= test_api_health()
    all_passed &= test_notion_client()
    all_passed &= test_api_endpoints()

    # Summary
    print(f"\n{'='*60}")
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print(f"✓ Notion API v{NOTION_API_VERSION} integration is working correctly")
    else:
        print("✗ SOME TESTS FAILED")
        print("  Check the output above for details")
    print(f"{'='*60}\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
