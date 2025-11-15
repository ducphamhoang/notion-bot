# 🚀 Notion Integration - Complete Walkthrough

This guide will walk you through integrating your Notion Bot API with a real Notion workspace.

**Time Required**: ~15 minutes  
**Current Status**: Ready to integrate ✅

---

## Phase 1: Set Up Notion Integration (5 minutes)

### Step 1.1: Create Notion Integration

1. **Open Notion Integrations Page**
   ```
   👉 Visit: https://www.notion.so/my-integrations
   ```

2. **Create New Integration**
   - Click **"+ New integration"** button
   
3. **Fill in Integration Details**
   - **Name**: `Notion Bot API` (or any name you prefer)
   - **Associated workspace**: Select your workspace
   - **Logo**: Optional (can skip)

4. **Set Capabilities** (check these boxes):
   - ✅ Read content
   - ✅ Update content
   - ✅ Insert content
   - ✅ Read user information (optional, for user mapping)

5. **Integration Type**
   - Select: **"Internal integration"** (for your private use)

6. **Submit**
   - Click **"Submit"** button

### Step 1.2: Copy API Key

1. After creating, you'll see the integration settings page
2. Find the **"Internal Integration Token"** section
3. Click **"Show"** then **"Copy"**
4. Your token looks like: `secret_XXXXXXXXXXXXXXXXXXXXX`

**⚠️ Keep this token safe! Don't share it publicly.**

---

## Phase 2: Create Notion Database (3 minutes)

### Step 2.1: Create a Task Database

1. **Open Notion** (your workspace)

2. **Create New Page**
   - Click **"+ New page"** in sidebar
   - Name it: `Bot Tasks` or `Task Manager`

3. **Create Database**
   - Type `/table` and select **"Table - Inline"**
   - Or type `/database` and select **"Table database"**

4. **Configure Database Properties**

   Your database should have these columns (properties):

   | Property Name | Type | Required | Notes |
   |---------------|------|----------|-------|
   | **Name** | Title | ✅ Yes | Task title (auto-created) |
   | **Status** | Select | ✅ Yes | Options: To Do, In Progress, Done |
   | **Priority** | Select | No | Options: Low, Medium, High |
   | **Due Date** | Date | No | Task deadline |
   | **Assignee** | Person | No | Who's responsible |
   | **Description** | Text | No | Task details |

   **To add properties**:
   - Click **"+"** button in table header
   - Select property type
   - Name the property

5. **Configure Status Options**
   - Click on **Status** column header → **"Edit property"**
   - Add these options:
     - `To Do` (or `todo`)
     - `In Progress` (or `in_progress`)
     - `Done` (or `done`)

6. **Configure Priority Options**
   - Click on **Priority** column header → **"Edit property"**
   - Add these options:
     - `Low`
     - `Medium`
     - `High`

### Step 2.2: Share Database with Integration

1. **Open your task database**
2. Click **"•••"** (three dots) in top-right corner
3. Select **"Connections"** or **"Add connections"**
4. Find **"Notion Bot API"** (your integration name)
5. Click to add it
6. Click **"Confirm"** if prompted

**✅ Checkpoint**: You should see your integration listed under database connections

### Step 2.3: Get Database ID

1. **Copy the database URL** from your browser
   - Example: `https://www.notion.so/workspace/12345678901234567890123456789012?v=...`

2. **Extract the Database ID** (32-character hex string)
   - It's the long string of letters/numbers after your workspace name
   - Example: `12345678901234567890123456789012`

3. **Save this ID** - you'll need it next!

---

## Phase 3: Configure Your Bot API (2 minutes)

### Step 3.1: Create .env File

1. **Navigate to project directory**
   ```bash
   cd /workspaces/notion-bot
   ```

2. **Copy example env file**
   ```bash
   cp .env.example .env
   ```

3. **Edit .env file**
   ```bash
   # Use any editor
   nano .env
   # or
   code .env
   ```

4. **Update with your credentials**
   ```bash
   # MongoDB Configuration
   MONGODB_URI=mongodb://localhost:27017/notion-bot

   # Notion API Configuration (UPDATE THESE!)
   NOTION_API_KEY=secret_YOUR_TOKEN_HERE_FROM_STEP_1
   NOTION_API_VERSION=2022-06-28

   # API Configuration
   API_HOST=0.0.0.0
   API_PORT=8000
   DEBUG=true
   CORS_ORIGINS=http://localhost:3000,http://localhost:8000

   # Logging
   LOG_LEVEL=INFO
   ```

5. **Replace**:
   - `secret_YOUR_TOKEN_HERE_FROM_STEP_1` with your actual Notion API key from Step 1.2
   - Keep `NOTION_API_VERSION=2022-06-28` as is

6. **Save the file** (Ctrl+O in nano, then Ctrl+X to exit)

---

## Phase 4: Start Services (2 minutes)

### Step 4.1: Start MongoDB

```bash
# If using Docker Compose
docker-compose up -d mongodb

# Or if MongoDB is already running locally
# Skip this step
```

**Verify MongoDB is running**:
```bash
docker ps | grep mongo
# Should show mongodb container running
```

### Step 4.2: Start the API Server

**Option A: Using Docker Compose (Recommended)**
```bash
docker-compose up -d
```

**Option B: Using Python directly**
```bash
# Make sure dependencies are installed
poetry install

# Run the server
poetry run python src/main.py
```

**Wait for startup** (~5 seconds)

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Phase 5: Test Integration (3 minutes)

### Step 5.1: Test Health Check

```bash
curl http://localhost:8000/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "notion": "connected",
  "timestamp": "2025-11-14T15:30:00Z"
}
```

**If you see errors**:
- `"notion": "error"` → Check your NOTION_API_KEY in .env
- `"database": "error"` → Check MongoDB is running
- Connection refused → Check API server is running on port 8000

### Step 5.2: Create Workspace Mapping

This tells your bot which Notion database to use:

```bash
curl -X POST http://localhost:8000/workspaces/ \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "web",
    "platform_id": "default",
    "notion_database_id": "YOUR_DATABASE_ID_FROM_STEP_2_3",
    "name": "Default Workspace"
  }'
```

**Replace** `YOUR_DATABASE_ID_FROM_STEP_2_3` with your actual database ID!

**Expected response**:
```json
{
  "id": "...",
  "platform": "web",
  "platform_id": "default",
  "notion_database_id": "YOUR_DATABASE_ID",
  "name": "Default Workspace",
  "created_at": "2025-11-14T15:30:00Z"
}
```

### Step 5.3: Create Your First Task! 🎉

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Task from API! 🚀",
    "notion_database_id": "YOUR_DATABASE_ID_FROM_STEP_2_3",
    "status": "To Do",
    "priority": "High",
    "description": "This task was created via the Notion Bot API"
  }'
```

**Replace** `YOUR_DATABASE_ID_FROM_STEP_2_3` with your database ID!

**Expected response**:
```json
{
  "notion_task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "notion_task_url": "https://www.notion.so/xxxxxxx",
  "created_at": "2025-11-14T15:30:00Z"
}
```

### Step 5.4: Verify in Notion

1. **Go back to your Notion database**
2. **Refresh the page** (F5 or Cmd+R)
3. **You should see your task!** 🎉
   - Title: "My First Task from API! 🚀"
   - Status: To Do
   - Priority: High

---

## Phase 6: Test Other Operations (Optional)

### List Tasks

```bash
curl "http://localhost:8000/tasks/?notion_database_id=YOUR_DATABASE_ID&limit=10"
```

### Update Task Status

First, get a task ID from the list, then:

```bash
curl -X PATCH http://localhost:8000/tasks/TASK_ID \
  -H "Content-Type: application/json" \
  -d '{
    "status": "In Progress"
  }'
```

### Delete Task

```bash
curl -X DELETE http://localhost:8000/tasks/TASK_ID
```

---

## Troubleshooting

### Problem: "notion": "error" in health check

**Cause**: Invalid API key or network issue

**Solutions**:
1. Verify your NOTION_API_KEY in .env file
2. Make sure the key starts with `secret_`
3. Check you copied the entire key (no spaces)
4. Restart the API server: `docker-compose restart` or `Ctrl+C` then rerun

### Problem: "object_not_found" when creating task

**Cause**: Integration doesn't have access to database

**Solutions**:
1. Go to your Notion database
2. Click "•••" → "Connections"
3. Make sure your integration is listed
4. If not, add it again (Step 2.2)

### Problem: "validation_error" for database_id

**Cause**: Invalid database ID format

**Solutions**:
1. Database ID must be 32 characters (no dashes)
2. Remove any dashes if present: `12345678-9012-3456-7890-123456789012` → `12345678901234567890123456789012`
3. Make sure you copied the ID from the URL correctly

### Problem: Task created but missing properties

**Cause**: Database doesn't have required properties

**Solutions**:
1. Check your database has these exact property names:
   - `Name` (Title type)
   - `Status` (Select type)
   - `Priority` (Select type)
2. Property names are case-sensitive!
3. Add missing properties to your database

### Problem: Server won't start

**Cause**: Port 8000 already in use or missing dependencies

**Solutions**:
```bash
# Check what's using port 8000
lsof -i :8000

# If something is using it, kill it or change API_PORT in .env

# Reinstall dependencies
poetry install

# Check MongoDB is running
docker ps | grep mongo
```

---

## Success Checklist ✅

Before proceeding to production, verify:

- ✅ Health check returns "healthy" status
- ✅ Notion connection shows "connected"
- ✅ Can create tasks via API
- ✅ Tasks appear in Notion database
- ✅ Can update task status
- ✅ Can list tasks
- ✅ Can delete tasks (archives them)
- ✅ All properties map correctly (status, priority, etc.)
- ✅ Error handling works (try invalid database ID)

---

## What's Next?

### For Development
- Add more task properties
- Implement user mapping
- Add task comments
- Implement webhooks

### For Production
- Set up monitoring (Prometheus/Grafana)
- Configure proper logging
- Set up backup procedures
- Review security settings
- Deploy to cloud (AWS/GCP/Azure)

### Documentation References
- **API Documentation**: `docs/API_DOCUMENTATION.md`
- **Deployment Guide**: `docs/DEPLOYMENT_GUIDE.md`
- **Operations Runbook**: `docs/OPERATIONS_RUNBOOK.md`

---

## Quick Reference

### Environment Variables
```bash
NOTION_API_KEY=secret_xxx        # Your integration token
NOTION_API_VERSION=2022-06-28    # API version
MONGODB_URI=mongodb://localhost:27017/notion-bot
API_PORT=8000
```

### Essential Commands
```bash
# Start services
docker-compose up -d

# Check health
curl http://localhost:8000/health

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Restart after config change
docker-compose restart
```

### API Endpoints
- **Health**: `GET /health`
- **Create Task**: `POST /tasks/`
- **List Tasks**: `GET /tasks/?notion_database_id=xxx`
- **Update Task**: `PATCH /tasks/{id}`
- **Delete Task**: `DELETE /tasks/{id}`
- **Workspaces**: `GET/POST /workspaces/`

---

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f api`
2. Review troubleshooting section above
3. Check Notion API status: https://status.notion.so/
4. Review `docs/OPERATIONS_RUNBOOK.md` for common issues

---

**Ready to integrate? Let's do this! 🚀**

Start with **Phase 1: Set Up Notion Integration** above.
