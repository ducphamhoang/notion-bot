# Migration Guide: Notion API 2025-09-03 (Latest)

## Why Migrate Now? ✅

You're **absolutely right** to want the latest API! Since you're just starting:

1. ✅ **No legacy code** - Start fresh with modern architecture
2. ✅ **Future-proof** - Old APIs will be deprecated eventually
3. ✅ **Better features** - Multi-source databases, improved data modeling
4. ✅ **Latest docs** - All new examples use 2025-09-03
5. ✅ **Avoid technical debt** - Don't build on deprecated foundations

---

## Key Concept Changes

### Before (2022-06-28): Simple Database Model
```
Database → Contains Pages
```

### After (2025-09-03): Multi-Source Model
```
Database → Contains Data Sources → Each Data Source contains Pages
```

**Why?** A single database can now have multiple data sources with different schemas.

---

## Required Code Changes

### Change 1: Update API Version in `.env`

```bash
# .env
NOTION_API_VERSION=2025-09-03  # ← Use latest
```

### Change 2: Modify NotionTaskService

The main changes are in `src/features/tasks/services/notion_task_service.py`:

#### 2a. Add Data Source Resolution Method

```python
async def _resolve_data_source_id(self, database_id: str) -> str:
    """
    Get the data_source_id from a database_id.

    In API 2025-09-03, databases contain data sources.
    We need the data_source_id for queries and page creation.
    """
    try:
        client = await self._get_client()

        # Retrieve database info
        db_info = await client.databases.retrieve(database_id=database_id)

        # Get data sources array
        data_sources = db_info.get("data_sources", [])

        if not data_sources:
            raise ValidationError(f"Database {database_id} has no data sources")

        # Use the first data source (most common case)
        # In future, you could support selecting specific data sources
        data_source_id = data_sources[0]["id"]
        data_source_name = data_sources[0].get("name", "Untitled")

        logger.info(
            f"Resolved database {database_id} to data source {data_source_id} "
            f"(name: {data_source_name})"
        )

        return data_source_id

    except APIResponseError as e:
        if e.status == 404:
            raise NotFoundError("database", database_id)
        raise NotionAPIError(
            f"Failed to resolve data source: {str(e)}",
            status_code=e.status
        )
```

#### 2b. Update `create_task()` Method

```python
async def create_task(self, request: CreateTaskRequest) -> CreateTaskResponse:
    """Create a new task in Notion database."""
    try:
        client = await self._get_client()

        # NEW: Resolve database_id to data_source_id
        data_source_id = await self._resolve_data_source_id(request.notion_database_id)

        # Get title property name
        resolver = get_database_resolver()
        title_property = await resolver.get_title_property_name(request.notion_database_id)

        # Resolve assignee if provided
        resolved_assignee_id = None
        if request.assignee_id:
            # ... (existing assignee resolution code)
            pass

        # Build properties
        properties = self._build_notion_properties(
            request, None, resolved_assignee_id, title_property
        )

        # CHANGED: Use data_source_id instead of database_id
        notion_page = await client.pages.create(
            parent={"data_source_id": data_source_id},  # ← CHANGED
            properties=properties
        )

        return CreateTaskResponse(
            notion_task_id=notion_page["id"],
            notion_task_url=notion_page["url"],
            created_at=datetime.fromisoformat(notion_page["created_time"])
        )

    except APIResponseError as e:
        # ... (existing error handling)
        pass
```

#### 2c. Update `list_tasks()` Method

The query endpoint changes from `/databases/{id}/query` to `/data_sources/{id}/query`:

```python
async def list_tasks(
    self,
    request: ListTasksRequest,
    property_mappings: Optional[Dict[str, str]] = None,
) -> ListTasksResponse:
    """Query tasks from Notion with filtering, sorting, and pagination."""
    try:
        client = await self._get_client()

        # NEW: Resolve to data_source_id
        data_source_id = await self._resolve_data_source_id(request.notion_database_id)

        resolved_mappings = self._resolve_property_mappings(property_mappings)
        notion_filter = self._build_list_filters(request, resolved_mappings)
        sorts = self._build_sort_params(request, resolved_mappings)

        # ... (pagination logic)

        while True:
            query_payload: dict[str, Any] = {
                # REMOVED: "database_id": request.notion_database_id,
                "page_size": min(page_size, 100),
            }
            if notion_filter:
                query_payload["filter"] = notion_filter
            if sorts:
                query_payload["sorts"] = sorts
            if cursor:
                query_payload["start_cursor"] = cursor

            # CHANGED: Use data_sources.query instead of databases.query
            response = await client.data_sources.query(
                data_source_id=data_source_id,  # ← CHANGED
                **query_payload
            )

            # ... (rest of pagination logic remains same)
```

### Change 3: Update Database Resolver

In `src/core/notion/database_resolver.py`, update to handle data sources:

```python
async def resolve_database_id(self, database_id: str) -> str:
    """
    Resolve a database ID to its primary data source ID.

    In API 2025-09-03, we need to work with data_source_id.
    """
    # Check cache
    if database_id in self._cache:
        cached = self._cache[database_id]
        return cached.get('data_source_id', database_id)

    try:
        client = await get_notion_client()

        # Retrieve database info
        db_info = await client.databases.retrieve(database_id=database_id)

        # Get data sources
        data_sources = db_info.get('data_sources', [])

        if not data_sources:
            logger.error(f"Database {database_id} has no data sources")
            return database_id

        # Use first data source
        data_source_id = data_sources[0]['id']
        data_source_name = data_sources[0].get('name', 'Untitled')

        logger.info(
            f"Resolved database {database_id} to data source {data_source_id} "
            f"({data_source_name})"
        )

        # Cache it
        self._cache[database_id] = {
            'data_source_id': data_source_id,
            'database_id': database_id,
            'name': data_source_name
        }

        return data_source_id

    except Exception as e:
        logger.error(f"Error resolving database {database_id}: {e}")
        return database_id
```

### Change 4: Update `get_database_schema()`

```python
async def get_database_schema(self, database_id: str) -> Dict[str, Any]:
    """Get the schema (properties) for a database."""
    try:
        client = await get_notion_client()

        # In 2025-09-03, retrieve database to get schema
        # Schema is still on the database object, not data source
        db_info = await client.databases.retrieve(database_id=database_id)

        if 'properties' in db_info:
            return db_info['properties']
        else:
            logger.warning(f"Database {database_id} has no properties schema")
            return {}

    except Exception as e:
        logger.error(f"Error getting schema for database {database_id}: {e}")
        return {}
```

---

## Python SDK Support

### Check Python SDK Version

The `notion-client` Python SDK needs to support API version 2025-09-03:

```bash
pip show notion-client
```

**Current version**: Check if >= 2.2.0 (approximate - verify on PyPI)

If needed, update:
```bash
pip install --upgrade notion-client
```

### Verify SDK Has data_sources Support

```python
from notion_client import AsyncClient

client = AsyncClient(auth="...", notion_version="2025-09-03")

# Check if these methods exist:
# client.data_sources.query(data_source_id="...")
# client.data_sources.retrieve(data_source_id="...")
```

---

## Migration Checklist

- [ ] Update `NOTION_API_VERSION=2025-09-03` in `.env`
- [ ] Upgrade `notion-client` Python package if needed
- [ ] Add `_resolve_data_source_id()` method to `NotionTaskService`
- [ ] Update `create_task()` to use `parent={"data_source_id": ...}`
- [ ] Update `list_tasks()` to use `client.data_sources.query()`
- [ ] Update `database_resolver.py` to resolve data_source_id
- [ ] Update test fixtures to use data_source_id
- [ ] Run integration tests
- [ ] Update API documentation

---

## Testing the Migration

1. **Update `.env`**:
   ```bash
   NOTION_API_VERSION=2025-09-03
   ```

2. **Restart services**:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

3. **Run diagnostic**:
   ```bash
   python test_notion_connection.py
   ```

4. **Test creating a task**:
   ```bash
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test with 2025-09-03 API",
       "notion_database_id": "your-database-id"
     }'
   ```

---

## Backward Compatibility Note

If you need to support both old and new API versions:

```python
async def create_task(self, request: CreateTaskRequest) -> CreateTaskResponse:
    settings = get_settings()

    if settings.notion_api_version >= "2025-09-03":
        # Use data_source_id
        data_source_id = await self._resolve_data_source_id(request.notion_database_id)
        parent = {"data_source_id": data_source_id}
    else:
        # Use database_id (old way)
        parent = {"database_id": request.notion_database_id}

    notion_page = await client.pages.create(
        parent=parent,
        properties=properties
    )
```

---

## Summary

**You're right to use the latest API!** The changes are:

1. **Database retrieval** → Get `data_sources` array → Extract `id`
2. **Create page**: `parent={"data_source_id": ...}` instead of `"database_id"`
3. **Query pages**: `client.data_sources.query(data_source_id)` instead of `client.databases.query(database_id)`
4. **Schema retrieval** → Still use `client.databases.retrieve()` (schema is on database)

The migration is straightforward and sets you up for success! 🚀
