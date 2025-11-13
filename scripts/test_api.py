#!/usr/bin/env python3
"""Simple script to test the Notion Bot API endpoints."""

import asyncio
import httpx
import json
from datetime import datetime, timedelta


async def test_api():
    """Test basic API functionality."""
    
    # Create test client
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        
        print("🔍 Testing API Endpoints")
        print("=" * 50)
        
        # Test health check
        try:
            response = await client.get("/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: {data['status']}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test root endpoint
        try:
            response = await client.get("/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API root: {data['name']} v{data['version']}")
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
        
        # Test workspace creation
        workspace_data = {
            "platform": "web",
            "platform_id": "test_workspace",
            "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
            "name": "Test Workspace"
        }
        
        try:
            response = await client.post("/workspaces/", json=workspace_data)
            if response.status_code == 201:
                data = response.json()
                print(f"✅ Workspace created: {data['name']} (ID: {data['id'][:8]}...)")
                workspace_id = data['id']
            else:
                print(f"❌ Workspace creation failed: {response.status_code}")
                if response.status_code >= 400:
                    error = response.json()
                    print(f"   Error: {error}")
                workspace_id = None
        except Exception as e:
            print(f"❌ Workspace creation error: {e}")
            workspace_id = None
        
        # Test task creation
        task_data = {
            "title": "Test Task from API",
            "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "priority": "High",
            "properties": {
                "Tags": {"multi_select": [{"name": "test"}]}
            }
        }
        
        try:
            response = await client.post("/tasks/", json=task_data)
            if response.status_code == 201:
                data = response.json()
                print(f"✅ Task created: {data['notion_task_url']}")
            else:
                print(f"❌ Task creation failed: {response.status_code}")
                if response.status_code >= 400:
                    error = response.json()
                    print(f"   Error: {error.get('error', {}).get('message', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Task creation error: {e}")
        
        # List workspaces
        try:
            response = await client.get("/workspaces/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {data['count']} workspaces")
                for ws in data['workspaces']:
                    print(f"   - {ws['name']} ({ws['platform']})")
            else:
                print(f"❌ List workspaces failed: {response.status_code}")
        except Exception as e:
            print(f"❌ List workspaces error: {e}")
        
        print("\n" + "=" * 50)
        print("🏁 Testing Complete")


if __name__ == "__main__":
    asyncio.run(test_api())
