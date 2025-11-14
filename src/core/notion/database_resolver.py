"""Notion database resolver for handling linked database views."""

from typing import Optional, Dict, Any
import logging

from notion_client import AsyncClient
from src.core.notion.client import get_notion_client

logger = logging.getLogger(__name__)


class DatabaseResolver:
    """Resolves database IDs and handles linked database views."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    async def resolve_database_id(self, database_id: str) -> str:
        """
        Resolve a database ID to its primary data source ID.

        In API version 2025-09-03, databases contain one or more data sources.
        This method extracts the first (primary) data source ID.

        Args:
            database_id: The database ID (UUID format)

        Returns:
            The data_source_id to use for operations
        """
        # Check cache first
        if database_id in self._cache:
            cached = self._cache[database_id]
            return cached.get('data_source_id', database_id)

        try:
            client = await get_notion_client()

            # Retrieve database info
            db_info = await client.databases.retrieve(database_id=database_id)

            # API 2025-09-03: Get data sources array
            data_sources = db_info.get('data_sources', [])

            if data_sources:
                # Extract the first data source ID
                data_source_id = data_sources[0]['id']
                data_source_name = data_sources[0].get('name', 'Untitled')

                logger.info(
                    f"Resolved database {database_id} to data source {data_source_id} "
                    f"(name: {data_source_name})"
                )

                # Cache the resolution
                self._cache[database_id] = {
                    'database_id': database_id,
                    'data_source_id': data_source_id,
                    'name': data_source_name,
                    'title': db_info.get('title', [{}])[0].get('plain_text', 'Untitled')
                }

                return data_source_id
            else:
                # No data sources found - this shouldn't happen in normal circumstances
                logger.warning(f"Database {database_id} has no data sources")

                # Cache with database_id as fallback
                self._cache[database_id] = {
                    'database_id': database_id,
                    'data_source_id': database_id,
                    'title': db_info.get('title', [{}])[0].get('plain_text', 'Untitled')
                }

                return database_id

        except Exception as e:
            logger.error(f"Error resolving database {database_id}: {e}")
            # If we can't resolve it, return the original ID and let it fail naturally
            return database_id
    
    async def get_database_schema(self, database_id: str) -> Dict[str, Any]:
        """
        Get the schema (properties) for a database.

        In API 2025-09-03, database.retrieve() may return empty properties.
        If this happens, we infer the schema by querying sample pages.

        Args:
            database_id: The database ID

        Returns:
            Dictionary of property name -> property info
        """
        # Check cache first
        if database_id in self._cache and 'properties' in self._cache[database_id]:
            return self._cache[database_id]['properties']

        # Resolve to source database first
        source_id = await self.resolve_database_id(database_id)

        try:
            client = await get_notion_client()
            db_info = await client.databases.retrieve(database_id=database_id)

            properties = db_info.get('properties', {})

            # API 2025-09-03: If database has no properties, infer from sample pages
            if not properties:
                logger.info(f"Database {database_id} has no properties at database level. Inferring from pages...")
                properties = await self._infer_schema_from_pages(source_id, database_id)

            # Cache the properties
            if database_id in self._cache:
                self._cache[database_id]['properties'] = properties
            else:
                self._cache[database_id] = {'properties': properties}

            return properties

        except Exception as e:
            logger.error(f"Error getting schema for database {database_id}: {e}")
            return {}

    async def _infer_schema_from_pages(self, data_source_id: str, database_id: str) -> Dict[str, Any]:
        """
        Infer database schema by querying sample pages.

        In API 2025-09-03, database-level properties may be empty,
        but pages still have properties with type information.

        Args:
            data_source_id: The data source ID to query
            database_id: The original database ID (for logging)

        Returns:
            Dictionary of property name -> property info inferred from pages
        """
        try:
            client = await get_notion_client()

            # Query a few pages to infer schema
            query_result = await client.data_sources.query(
                data_source_id=data_source_id,
                page_size=5
            )

            pages = query_result.get("results", [])

            if not pages:
                logger.warning(f"No pages found in data source {data_source_id} to infer schema")
                return {}

            # Extract properties from first page
            first_page = pages[0]
            page_properties = first_page.get("properties", {})

            if not page_properties:
                logger.warning(f"First page in data source {data_source_id} has no properties")
                return {}

            # Build schema dictionary from page properties
            schema = {}
            for prop_name, prop_value in page_properties.items():
                prop_type = prop_value.get("type")
                prop_id = prop_value.get("id")

                schema[prop_name] = {
                    "id": prop_id,
                    "type": prop_type,
                    # Note: We don't have full schema details like select options,
                    # but we have enough to identify property names and types
                }

            logger.info(
                f"Inferred {len(schema)} properties from pages in data source {data_source_id}: "
                f"{list(schema.keys())}"
            )

            return schema

        except Exception as e:
            logger.error(f"Error inferring schema from pages for data source {data_source_id}: {e}")
            return {}
    
    async def get_title_property_name(self, database_id: str) -> str:
        """
        Get the name of the title property for a database.
        
        Args:
            database_id: The database ID
            
        Returns:
            The name of the title property (default: "Name")
        """
        schema = await self.get_database_schema(database_id)
        
        # Find the title property
        for prop_name, prop_info in schema.items():
            if prop_info.get('type') == 'title':
                logger.debug(f"Found title property '{prop_name}' for database {database_id}")
                return prop_name
        
        # Default fallback
        logger.warning(f"No title property found for database {database_id}, using 'Name'")
        return "Name"
    
    def clear_cache(self):
        """Clear the resolution cache."""
        self._cache.clear()


# Global singleton instance
_resolver: Optional[DatabaseResolver] = None


def get_database_resolver() -> DatabaseResolver:
    """Get the global database resolver instance."""
    global _resolver
    if _resolver is None:
        _resolver = DatabaseResolver()
    return _resolver
