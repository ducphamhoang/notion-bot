"""Repository for workspace database operations."""

import logging
from datetime import datetime
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from src.core.database.connection import DatabaseConnection
from src.core.errors.exceptions import NotFoundError, ConflictError, InternalError
from src.features.workspaces.models import Workspace, WorkspaceCreate, WorkspaceUpdate

logger = logging.getLogger(__name__)


class WorkspaceRepository:
    """Repository for workspace CRUD operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase | None = None):
        self.db = database
        self._collection: Optional[AsyncIOMotorCollection] = None
    
    @property
    async def collection(self) -> AsyncIOMotorCollection:
        """Get the workspaces collection, ensuring database is connected."""
        if self.db is None:
            self.db = await DatabaseConnection.get_database()
        if self._collection is None:
            self._collection = self.db.workspaces
        return self._collection
    
    async def find_by_platform_id(self, platform: str, platform_id: str) -> Optional[Workspace]:
        """Find workspace by platform and platform_id."""
        try:
            doc = await (await self.collection).find_one({
                "platform": platform,
                "platform_id": platform_id
            })
            
            if doc:
                return Workspace(**doc)
            return None
            
        except Exception:
            # Log error but don't expose internal details
            logger.error(f"Database error finding workspace {platform}/{platform_id}")
            raise
    
    async def create(self, workspace_data: WorkspaceCreate) -> Workspace:
        """Create a new workspace mapping."""
        from datetime import datetime
        
        workspace_dict = workspace_data.dict()
        
        # Set default property_mappings if None
        if workspace_dict.get("property_mappings") is None:
            workspace_dict["property_mappings"] = {
                "title": "Name",
                "due_date": "Due Date",
                "priority": "Priority",
                "assignee": "Assignee",
                "status": "Status"
            }
        
        # Add timestamps
        workspace_dict["created_at"] = datetime.utcnow()
        workspace_dict["updated_at"] = datetime.utcnow()
        
        try:
            # Check for duplicate first
            existing = await self.find_by_platform_id(
                workspace_dict["platform"],
                workspace_dict["platform_id"]
            )
            if existing:
                raise ConflictError(
                    f"Workspace already exists for {workspace_dict['platform']}/{workspace_dict['platform_id']}",
                    {"platform": workspace_dict["platform"], "platform_id": workspace_dict["platform_id"]}
                )
            
            # Insert new document
            result = await (await self.collection).insert_one(workspace_dict)
            
            # Retrieve the created document
            created = await (await self.collection).find_one({"_id": result.inserted_id})
            
            if created:
                return Workspace(**created)
            else:
                raise InternalError("Failed to create workspace")
                
        except ConflictError:
            raise
        except Exception as e:
            logger.error(f"Database error creating workspace {workspace_dict}: {type(e).__name__}: {e}")
            raise InternalError(f"Failed to create workspace: {str(e)}")
    
    async def get_by_id(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by MongoDB _id."""
        try:
            doc = await (await self.collection).find_one({"_id": ObjectId(workspace_id)})
            
            if doc:
                return Workspace(**doc)
            return None
            
        except ValueError:
            # Invalid ObjectId
            raise NotFoundError("workspace", workspace_id)
        except Exception:
            logger.error(f"Database error getting workspace {workspace_id}")
            raise
    
    async def update(self, workspace_id: str, update_data: WorkspaceUpdate) -> Optional[Workspace]:
        """Update workspace by ID."""
        try:
            # Convert update_data to dict, excluding None values
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            if not update_dict:
                # No fields to update
                return await self.get_by_id(workspace_id)
            
            # Add updated_at timestamp
            update_dict["updated_at"] = datetime.utcnow()
            
            result = await (await self.collection).update_one(
                {"_id": ObjectId(workspace_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                return await self.get_by_id(workspace_id)
            elif result.matched_count == 0:
                return None  # Document not found
            else:
                # Document matched but no actual changes
                return await self.get_by_id(workspace_id)
                
        except ValueError:
            raise NotFoundError("workspace", workspace_id)
        except Exception:
            logger.error(f"Database error updating workspace {workspace_id}")
            raise InternalError("Failed to update workspace")
    
    async def delete(self, workspace_id: str) -> bool:
        """Delete workspace by ID."""
        try:
            result = await (await self.collection).delete_one({"_id": ObjectId(workspace_id)})
            return result.deleted_count > 0
            
        except ValueError:
            raise NotFoundError("workspace", workspace_id)
        except Exception:
            logger.error(f"Database error deleting workspace {workspace_id}")
            raise InternalError("Failed to delete workspace")
    
    async def list_all(self, platform: Optional[str] = None) -> list[Workspace]:
        """List all workspaces, optionally filtered by platform."""
        try:
            filter_dict = {}
            if platform:
                filter_dict["platform"] = platform
            
            cursor = (await self.collection).find(filter_dict).sort("created_at", -1)
            
            workspaces = []
            async for doc in cursor:
                workspaces.append(Workspace(**doc))
            
            return workspaces
            
        except Exception:
            logger.error("Database error listing workspaces")
            raise InternalError("Failed to list workspaces")
