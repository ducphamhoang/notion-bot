#!/usr/bin/env python3
"""Test script to diagnose Notion API connection issues."""

import asyncio
import os
import sys
from dotenv import load_dotenv
from notion_client import AsyncClient


async def test_connection():
    """Run comprehensive Notion API connection tests."""
    # Load .env file, overriding any existing environment variables
    load_dotenv(override=True)

    # Get credentials
    api_key = os.getenv("NOTION_API_KEY")
    api_version = os.getenv("NOTION_API_VERSION", "2022-06-28")

    print("=" * 60)
    print("Notion API Connection Diagnostic")
    print("=" * 60)

    # Validate API key format
    if not api_key:
        print("❌ NOTION_API_KEY not found in environment!")
        print("\nMake sure you have a .env file with:")
        print("  NOTION_API_KEY=secret_your_token_here")
        return False

    if not api_key.startswith("secret_") and not api_key.startswith("ntn_"):
        print(f"⚠️  WARNING: API key format may be incorrect")
        print(f"   Your key: {api_key[:20]}...")
        print(f"   Expected: secret_XXX... or ntn_XXX...")

    print(f"\n✅ API Key found: {api_key[:20]}... (truncated)")
    print(f"✅ API Version: {api_version}")

    # Initialize client with correct version
    client = AsyncClient(
        auth=api_key,
        notion_version=api_version
    )

    print(f"\n📌 Using Notion API Version: {api_version}")
    if api_version >= "2025-09-03":
        print("   ℹ️  This version uses data sources (multi-source databases)")

    try:
        # Test 1: Search for databases
        print("\n" + "-" * 60)
        print("[Test 1] Searching for accessible databases...")
        print("-" * 60)

        # API 2025-09-03: Search filter uses "data_source" instead of "database"
        if api_version >= "2025-09-03":
            search_filter = {"property": "object", "value": "data_source"}
        else:
            search_filter = {"property": "object", "value": "database"}

        search_result = await client.search(filter=search_filter)
        databases = search_result.get("results", [])

        if not databases:
            print("❌ No databases found!")
            print("\nPossible reasons:")
            print("1. No databases exist in your Notion workspace")
            print("2. Databases are not shared with this integration")
            print("\nTo fix:")
            print("   a) Open a database in Notion")
            print("   b) Click '•••' menu → 'Add connections'")
            print("   c) Select your integration")
            print("   d) Click 'Confirm'")
            return False

        print(f"✅ Found {len(databases)} accessible database(s):\n")

        for idx, db in enumerate(databases[:5], 1):
            title = db.get("title", [{}])[0].get("plain_text", "Untitled")
            db_id = db.get("id")
            print(f"  {idx}. {title}")
            print(f"     ID: {db_id}")

        if len(databases) > 5:
            print(f"\n  ... and {len(databases) - 5} more")

        # Test 2: Retrieve database/data source details
        test_item = databases[0]
        test_item_id = test_item["id"]
        test_item_title = test_item.get("title", [{}])[0].get("plain_text", "Untitled")

        print("\n" + "-" * 60)
        print(f"[Test 2] Retrieving details...")
        print("-" * 60)
        print(f"Testing with: {test_item_title} ({test_item_id})")

        # API 2025-09-03: Search returns data sources, need to retrieve data source
        if api_version >= "2025-09-03":
            # Retrieve data source to get parent database ID
            ds_info = await client.data_sources.retrieve(data_source_id=test_item_id)
            print(f"✅ Successfully retrieved data source")

            # Debug: Show data source structure
            import json
            print(f"   Data source structure: {json.dumps(ds_info, indent=2, default=str)[:500]}")

            # Get parent database - try different field names
            test_db_id = (
                ds_info.get("database_id") or
                ds_info.get("parent", {}).get("database_id") or
                ds_info.get("database", {}).get("id")
            )

            if not test_db_id:
                # Fallback: use the data source directly as the database
                print(f"   ⚠️  No parent database_id found, using data source as database")
                test_db_id = test_item_id
                db_info = ds_info  # Use data source info as database info
            else:
                print(f"   Parent Database ID: {test_db_id}")
                # Now retrieve the actual database
                db_info = await client.databases.retrieve(database_id=test_db_id)

            # Use data source ID for subsequent operations
            test_data_source_id = test_item_id
        else:
            # Old API: Search returns databases directly
            test_db_id = test_item_id
            db_info = await client.databases.retrieve(database_id=test_db_id)

        print(f"✅ Successfully retrieved database")
        print(f"   Database Title: {db_info.get('title', [{}])[0].get('plain_text', 'Untitled')}")

        # Show data sources (API 2025-09-03+)
        data_sources = db_info.get("data_sources", [])
        if api_version >= "2025-09-03":
            if data_sources:
                print(f"\n  Data Sources ({len(data_sources)}):")
                for idx, ds in enumerate(data_sources, 1):
                    ds_id = ds.get("id")
                    ds_name = ds.get("name", "Untitled")
                    is_test_ds = " ← TESTING WITH THIS" if ds_id == test_data_source_id else ""
                    print(f"    {idx}. {ds_name}{is_test_ds}")
                    print(f"       ID: {ds_id}")

        print(f"\n  Database Properties:")
        properties = db_info.get("properties", {})

        for prop_name, prop_info in list(properties.items())[:10]:
            prop_type = prop_info.get("type", "unknown")
            print(f"    - {prop_name}: {prop_type}")

        if len(properties) > 10:
            print(f"    ... and {len(properties) - 10} more properties")

        # Test 3: Query the database/data source
        print("\n" + "-" * 60)
        print("[Test 3] Querying database pages...")
        print("-" * 60)

        # API 2025-09-03: Use data_sources.query() instead of databases.query()
        if api_version >= "2025-09-03":
            # Already have test_data_source_id from Test 2
            print(f"Using data source: {test_data_source_id}")
            query_result = await client.data_sources.query(
                data_source_id=test_data_source_id,
                page_size=5
            )
        else:
            # Fallback for older API versions
            query_result = await client.databases.query(
                database_id=test_db_id,
                page_size=5
            )

        pages = query_result.get("results", [])
        print(f"✅ Query successful! Found {len(pages)} page(s)\n")

        for idx, page in enumerate(pages, 1):
            # Try to extract title from properties
            page_props = page.get("properties", {})
            page_title = "Untitled"

            # Find title property
            for prop_name, prop_value in page_props.items():
                if prop_value.get("type") == "title":
                    title_content = prop_value.get("title", [])
                    if title_content:
                        page_title = title_content[0].get("plain_text", "Untitled")
                    break

            print(f"  {idx}. {page_title}")
            print(f"     URL: {page.get('url', 'N/A')}")

        # Test 4: Create a test page
        print("\n" + "-" * 60)
        print(f"[Test 4] Creating a test page...")
        print("-" * 60)

        # Find the title property name from the database schema
        title_prop_name = None
        for prop_name, prop_info in properties.items():
            if prop_info.get("type") == "title":
                title_prop_name = prop_name
                break

        if not title_prop_name:
            print(f"⚠️  No title property found in database schema")
            print(f"   Available properties: {list(properties.keys())[:5]}")
            print(f"   Skipping page creation test")
            # Skip to summary
            print("\n" + "=" * 60)
            print("✅ TESTS PASSED (page creation skipped)")
            print("=" * 60)
            print("\nYour Notion integration is working!")
            print(f"\n📋 Database Information:")
            print(f"   Database ID: {test_db_id}")
            if api_version >= "2025-09-03":
                print(f"   Data Source ID: {test_data_source_id}")
                print(f"   Data Source Name: {test_item_title}")
            print(f"\n✅ Ready to use! Configuration:")
            print(f"   notion_database_id: {test_db_id}")
            return True

        print(f"Using title property: '{title_prop_name}'")

        # API 2025-09-03: Use data_source_id instead of database_id
        if api_version >= "2025-09-03":
            parent_config = {"data_source_id": test_data_source_id}
            print(f"Creating page in data source: {test_data_source_id}")
        else:
            parent_config = {"database_id": test_db_id}

        new_page = await client.pages.create(
            parent=parent_config,
            properties={
                title_prop_name: {
                    "title": [{"text": {"content": "🧪 API Connection Test (Safe to Delete)"}}]
                }
            }
        )

        print(f"✅ Successfully created test page!")
        print(f"   Page ID: {new_page.get('id')}")
        print(f"   URL: {new_page.get('url')}")

        # Test 5: Archive the test page
        print("\n" + "-" * 60)
        print("[Test 5] Cleaning up test page...")
        print("-" * 60)

        await client.pages.update(
            page_id=new_page["id"],
            archived=True
        )

        print(f"✅ Test page archived successfully")

        # Summary
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour Notion integration is working correctly!")
        print(f"\n📋 Database Information:")
        print(f"   Database ID: {test_db_id}")

        if api_version >= "2025-09-03":
            print(f"   Data Source ID: {test_data_source_id}")
            print(f"   Data Source Name: {test_item_title}")
            print(f"\n   ℹ️  With API 2025-09-03, your app will automatically")
            print(f"      resolve database_id → data_source_id")

        print("\n✅ Ready to use! Your workspace configuration should be:")
        print(f"   notion_database_id: {test_db_id}")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        print("=" * 60)
        print("Troubleshooting Guide")
        print("=" * 60)

        error_str = str(e).lower()

        if "unauthorized" in error_str or "invalid" in error_str:
            print("\n🔑 API Key Issue:")
            print("1. Go to https://www.notion.so/my-integrations")
            print("2. Click on your integration")
            print("3. Copy the 'Internal Integration Token'")
            print("4. Update NOTION_API_KEY in your .env file")

        elif "404" in error_str or "not found" in error_str:
            print("\n🔗 Database Sharing Issue:")
            print("1. Open your database in Notion")
            print("2. Click the '•••' menu (top right)")
            print("3. Select 'Add connections'")
            print("4. Find your integration and click it")
            print("5. Click 'Confirm'")

        elif "403" in error_str or "restricted" in error_str:
            print("\n🔒 Permission Issue:")
            print("1. Go to https://www.notion.so/my-integrations")
            print("2. Click on your integration")
            print("3. Under 'Capabilities', ensure these are checked:")
            print("   ✅ Read content")
            print("   ✅ Update content")
            print("   ✅ Insert content")
            print("4. Save changes")
            print("5. Re-share your database with the integration")

        elif "rate_limit" in error_str or "429" in error_str:
            print("\n⏱️  Rate Limit Issue:")
            print("You've made too many requests. Wait a moment and try again.")

        else:
            print("\n❓ Unknown Error:")
            print("Check the error message above and:")
            print("1. Verify your .env file is loaded correctly")
            print("2. Ensure Docker containers can access the .env file")
            print("3. Check Notion API status: https://status.notion.so")

        print("\n📖 For more help, see: NOTION_DATABASE_DIAGNOSTIC.md")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
