# Notion Database Connection Diagnostic

## Issues Identified

### 🔴 Critical: API Version Not Being Passed to Client

**Problem**: Your `AsyncClient` is NOT using the `notion_api_version` from settings.

**Current Code** (`src/core/notion/client.py`):
```python
_notion_client = AsyncClient(
    auth=settings.notion_api_key,
    # Missing: notion_version parameter!
)
```

**What's Happening**:
- Settings has: `NOTION_API_VERSION=2022-10-28`
- AsyncClient receives: `None` (defaults to `2022-06-28`)
- **You're using an older API version than configured!**

**Fix Required**:
```python
_notion_client = AsyncClient(
    auth=settings.notion_api_key,
    notion_version=settings.notion_api_version  # Add this line
)
```

---

## ⚠️ Important: Notion API Breaking Changes (2025-09-03)

Notion released API version `2025-09-03` with **BREAKING CHANGES**:

### What Changed:
1. **Database queries deprecated** → Use "data sources" instead
2. **`database_id` → `data_source_id`** for creating pages
3. **New endpoint**: `POST /v1/data_sources/{data_source_id}/query`

### Should You Upgrade?

**For Now: NO** - Stay on `2022-06-28` or `2022-10-28`
- Your current code works with these versions
- The old endpoints still function
- Upgrading requires significant code changes

**In Future: YES** - Plan migration for production
- The deprecated endpoints will eventually be removed
- New features require the latest API version

---

## Common Database Connection Issues

### Issue 1: Database Not Shared with Integration ⭐ MOST COMMON

**Symptoms**:
```
404 Not Found: "database_id" does not exist
```

**Solution**:
1. Open your Notion database
2. Click the **"•••"** menu (top right)
3. Click **"Add connections"** or **"Connections"**
4. Find and select your integration: **"Notion Bot API"**
5. Click **"Confirm"**

**Visual Check**:
- You should see your integration name listed under "Connections" in the database menu

---

### Issue 2: Invalid Database ID

**Symptoms**:
```
validation_error: database_id is not a valid uuid
```

**How to Get Correct Database ID**:

1. **Open your database as a full page**
2. **Copy the URL**:
   ```
   https://www.notion.so/workspace/a1b2c3d4e5f6...?v=view123
   ```
3. **Extract the database ID** (32-character hex between last `/` and `?`):
   ```
   a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6
   ```
4. **Format with dashes** (8-4-4-4-12):
   ```
   a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6
   ```

**Alternative: Use Notion's Search API**:
```bash
curl 'https://api.notion.com/v1/search' \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H 'Notion-Version: 2022-06-28' \
  -H 'Content-Type: application/json' \
  --data '{"filter":{"property":"object","value":"database"}}'
```

---

### Issue 3: Integration Lacks Permissions

**Symptoms**:
```
API responded with status 403: {"object":"error","status":403,"code":"restricted_resource"}
```

**Solution**:
1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click on your integration
3. **Verify Capabilities are enabled**:
   - ✅ Read content
   - ✅ Update content
   - ✅ Insert content
   - ✅ Read user information (for assignees)
4. **Save changes**
5. **Re-share the database** with the integration

---

### Issue 4: Invalid API Key

**Symptoms**:
```
unauthorized: "API token is invalid"
```

**Solution**:
1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click on your integration
3. Under **"Internal Integration Token"**, click **"Show"** then **"Copy"**
4. Update your `.env` file:
   ```bash
   NOTION_API_KEY=secret_XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
5. **Restart your application**

---

## Quick Diagnostic Test

Create a test script to verify everything works:

```python
# test_notion_connection.py
import asyncio
from notion_client import AsyncClient
import os
from dotenv import load_dotenv

async def test_connection():
    load_dotenv()

    # Get credentials
    api_key = os.getenv("NOTION_API_KEY")
    api_version = os.getenv("NOTION_API_VERSION", "2022-06-28")

    print(f"API Key: {api_key[:20]}... (truncated)")
    print(f"API Version: {api_version}")

    # Initialize client with correct version
    client = AsyncClient(
        auth=api_key,
        notion_version=api_version  # FIX: Add this parameter
    )

    try:
        # Test 1: Search for databases
        print("\n[Test 1] Searching for databases...")
        search_result = await client.search(
            filter={"property": "object", "value": "database"}
        )
        databases = search_result.get("results", [])
        print(f"✅ Found {len(databases)} database(s)")

        for db in databases[:5]:  # Show first 5
            title = db.get("title", [{}])[0].get("plain_text", "Untitled")
            db_id = db.get("id")
            print(f"  - {title}: {db_id}")

        # Test 2: Try to retrieve a specific database
        if databases:
            test_db_id = databases[0]["id"]
            print(f"\n[Test 2] Retrieving database {test_db_id}...")
            db_info = await client.databases.retrieve(database_id=test_db_id)
            print(f"✅ Successfully retrieved: {db_info.get('title', [{}])[0].get('plain_text', 'Untitled')}")

            # Test 3: Try to query the database
            print(f"\n[Test 3] Querying database...")
            query_result = await client.databases.query(
                database_id=test_db_id,
                page_size=1
            )
            print(f"✅ Query successful! Found {len(query_result.get('results', []))} page(s)")
        else:
            print("\n⚠️ No databases found. Make sure:")
            print("   1. You've created a database in Notion")
            print("   2. The database is shared with your integration")

        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your NOTION_API_KEY is correct")
        print("2. Ensure databases are shared with your integration")
        print("3. Verify integration has required permissions")

if __name__ == "__main__":
    asyncio.run(test_connection())
```

**Run the test**:
```bash
python test_notion_connection.py
```

---

## Required Code Fixes

### Fix 1: Update `src/core/notion/client.py`

```python
async def get_notion_client() -> AsyncClient:
    """Get Notion client instance, creating if needed."""
    global _notion_client

    if _notion_client is None:
        async with _client_lock:
            if _notion_client is None:
                settings = get_settings()

                _notion_client = AsyncClient(
                    auth=settings.notion_api_key,
                    notion_version=settings.notion_api_version  # ← ADD THIS LINE
                )

    return _notion_client
```

### Fix 2: Verify `.env` Configuration

```bash
# Notion API Configuration
NOTION_API_KEY=secret_your_actual_integration_token_here
NOTION_API_VERSION=2022-06-28  # Use 2022-06-28 for stability

# Or use 2022-10-28 if you need newer features:
# NOTION_API_VERSION=2022-10-28
```

---

## Verification Checklist

- [ ] API key starts with `secret_` and is copied correctly
- [ ] Database is shared with the integration (check "Connections" in database menu)
- [ ] Integration has required capabilities enabled
- [ ] `notion_version` parameter is passed to AsyncClient
- [ ] `.env` file is loaded correctly (check `docker-compose` volumes)
- [ ] Application restarted after `.env` changes
- [ ] Database ID is in correct UUID format (with dashes)

---

## Testing Your Fix

After applying the fixes:

1. **Restart the API**:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

2. **Check health endpoint**:
   ```bash
   curl http://localhost:8000/health
   ```

3. **Test creating a task**:
   ```bash
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test Task",
       "notion_database_id": "your-database-id-here"
     }'
   ```

4. **Expected Response**:
   ```json
   {
     "notion_task_id": "...",
     "notion_task_url": "https://notion.so/...",
     "created_at": "2025-01-14T..."
   }
   ```

---

## Future: Migrating to API Version 2025-09-03

When you're ready to upgrade (not urgent):

### Changes Required:

1. **Get data source IDs** instead of database IDs
2. **Update query calls**:
   ```python
   # OLD (deprecated):
   await client.databases.query(database_id=db_id)

   # NEW (2025-09-03+):
   await client.data_sources.query(data_source_id=ds_id)
   ```

3. **Update page creation**:
   ```python
   # OLD:
   await client.pages.create(
       parent={"database_id": db_id},
       properties=...
   )

   # NEW:
   await client.pages.create(
       parent={"data_source_id": ds_id},
       properties=...
   )
   ```

**Reference**: https://developers.notion.com/docs/upgrade-guide-2025-09-03

---

## Summary

**Immediate Actions**:
1. ✅ Add `notion_version=settings.notion_api_version` to AsyncClient initialization
2. ✅ Share your database with the integration in Notion UI
3. ✅ Run the diagnostic test script
4. ✅ Restart your application

**Root Cause**: Most likely the database isn't shared with your integration, combined with the API version not being passed to the client.

Good luck! Let me know if you hit any other issues. 🚀
