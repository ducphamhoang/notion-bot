#!/usr/bin/env python3
"""Diagnose database schema by querying existing pages."""

import asyncio
import os
import json
from dotenv import load_dotenv
from notion_client import AsyncClient


async def diagnose_schema():
    """Query data source pages to infer schema."""
    load_dotenv(override=True)

    api_key = os.getenv("NOTION_API_KEY")
    api_version = os.getenv("NOTION_API_VERSION", "2022-06-28")

    database_id = "2874d13d-7750-8060-871d-fa4bd5dbbd09"

    print("=" * 60)
    print("Database Schema Diagnostic")
    print("=" * 60)
    print(f"\nDatabase ID: {database_id}")
    print(f"API Version: {api_version}\n")

    client = AsyncClient(auth=api_key, notion_version=api_version)

    try:
        # Step 1: Retrieve database info
        print("[Step 1] Retrieving database info...")
        db_info = await client.databases.retrieve(database_id=database_id)

        print(f"Database Title: {db_info.get('title', [{}])[0].get('plain_text', 'Untitled')}")
        print(f"Database Object: {db_info.get('object')}")

        # Check properties from database
        db_properties = db_info.get("properties", {})
        print(f"\nDatabase-level properties: {len(db_properties)}")
        if db_properties:
            for prop_name, prop_info in db_properties.items():
                print(f"  - {prop_name}: {prop_info.get('type')}")
        else:
            print("  ❌ No properties found at database level")

        # Check data sources
        data_sources = db_info.get("data_sources", [])
        print(f"\nData sources: {len(data_sources)}")

        if not data_sources:
            print("  ❌ No data sources found!")
            return

        data_source_id = data_sources[0]["id"]
        data_source_name = data_sources[0].get("name", "Untitled")
        print(f"  Using: {data_source_name} ({data_source_id})")

        # Step 2: Query data source for pages
        print(f"\n[Step 2] Querying data source for existing pages...")
        query_result = await client.data_sources.query(
            data_source_id=data_source_id,
            page_size=5
        )

        pages = query_result.get("results", [])
        print(f"Found {len(pages)} existing page(s)")

        if not pages:
            print("  ❌ No pages found in data source!")
            print("\n💡 This database appears to be empty.")
            print("   You may need to:")
            print("   1. Create a page manually in Notion first")
            print("   2. Or check if this is the correct database")
            return

        # Step 3: Inspect properties from first page
        print(f"\n[Step 3] Inspecting properties from existing page...")
        first_page = pages[0]
        page_properties = first_page.get("properties", {})

        print(f"\nFound {len(page_properties)} properties on page:")
        print("\nProperty Details:")
        print("-" * 60)

        property_summary = {}
        for prop_name, prop_value in page_properties.items():
            prop_type = prop_value.get("type")
            property_summary[prop_name] = prop_type

            print(f"\n📌 {prop_name}")
            print(f"   Type: {prop_type}")
            print(f"   ID: {prop_value.get('id')}")

            # Show value based on type
            if prop_type == "title":
                title_content = prop_value.get("title", [])
                if title_content:
                    text = title_content[0].get("plain_text", "")
                    print(f"   Value: '{text}'")
            elif prop_type == "rich_text":
                rt_content = prop_value.get("rich_text", [])
                if rt_content:
                    text = rt_content[0].get("plain_text", "")
                    print(f"   Value: '{text}'")
            elif prop_type == "select":
                select_val = prop_value.get("select")
                if select_val:
                    print(f"   Value: '{select_val.get('name')}'")
            elif prop_type == "status":
                status_val = prop_value.get("status")
                if status_val:
                    print(f"   Value: '{status_val.get('name')}'")
            elif prop_type == "date":
                date_val = prop_value.get("date")
                if date_val:
                    print(f"   Value: {date_val}")
            elif prop_type == "people":
                people = prop_value.get("people", [])
                print(f"   Value: {len(people)} person/people")

        # Step 4: Show other pages
        if len(pages) > 1:
            print("\n" + "-" * 60)
            print(f"\nOther pages in database:")
            for idx, page in enumerate(pages[1:], 2):
                props = page.get("properties", {})

                # Find title
                title = "Untitled"
                for prop_name, prop_value in props.items():
                    if prop_value.get("type") == "title":
                        title_content = prop_value.get("title", [])
                        if title_content:
                            title = title_content[0].get("plain_text", "Untitled")
                        break

                print(f"  {idx}. {title}")
                print(f"     URL: {page.get('url')}")

        # Summary
        print("\n" + "=" * 60)
        print("✅ SCHEMA INFERRED FROM EXISTING PAGES")
        print("=" * 60)
        print(f"\nTo create a new task, use these properties:")
        print(json.dumps(property_summary, indent=2))

        # Find title property
        title_prop = None
        for prop_name, prop_type in property_summary.items():
            if prop_type == "title":
                title_prop = prop_name
                break

        if title_prop:
            print(f"\n💡 Title property: '{title_prop}'")
            print(f"\nExample API call:")
            print(f"""
curl -X POST http://localhost:8000/tasks/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "title": "Test Task",
    "notion_database_id": "{database_id}"
  }}'
""")
        else:
            print("\n⚠️  WARNING: No title property found!")
            print("   This database may not support standard task creation.")

        return property_summary

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(diagnose_schema())
