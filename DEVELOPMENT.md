# Development Guide

## Quick Start

1. **Set up Python environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
# Install poetry for dependency management (optional)
pip install poetry

# Or install directly with pip
pip install fastapi uvicorn pydantic pydantic-settings motor notion-client python-multipart structlog
pip install pytest pytest-asyncio httpx black isort mypy ruff
```

3. **Start MongoDB:**
```bash
docker-compose up -d mongodb
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your NOTION_API_KEY
```

5. **Run the API:**
```bash
python src/main.py
```

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Run Specific Tests
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only  
pytest tests/integration/

# Specific test class
pytest tests/unit/test_tasks_service.py::TestNotionTaskService
```

## Code Quality

### Format Code
```bash
black src/
isort src/
```

### Lint and Type Check
```bash
ruff check src/
mypy src/
```

### All Quality Checks
```bash
black src/ && isort src/ && ruff check src/ && mypy src/
```

## API Usage

### Start the Server
```bash
source venv/bin/activate
python src/main.py
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Create workspace
curl -X POST http://localhost:8000/workspaces/ \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "web",
    "platform_id": "test_workspace", 
    "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
    "name": "Test Workspace"
  }'

# Create task
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
    "priority": "High"
  }'

# List workspaces
curl http://localhost:8000/workspaces/
```

## Architecture Overview

### Directory Structure
```
src/
├── core/                    # Shared infrastructure
│   ├── database/           # MongoDB connection management
│   ├── notion/             # Notion SDK wrapper and rate limiting
│   └── errors/             # Custom exceptions and error handling
├── config/                 # Settings and configuration
├── features/               # Business features (vertical slices)
│   ├── tasks/             # Task CRUD operations
│   └── workspaces/        # Workspace-to-Notion mappings
└── main.py                # Application entrypoint
```

### Feature Structure
Each feature follows this pattern:
```
features/example/
├── routes.py              # API endpoints (FastAPI router)
├── services/              # Business logic layer
├── dto/                   # Request/response models
├── models.py              # Database schema
└── repository.py          # Database operations
```

### Key Principles
1. **Feature-first organization** - Group code by business domain
2. **Clean architecture** - Separate infrastructure from business logic
3. **Dependency injection** - Easy testing and modularity
4. **Error handling** - Standardized error responses
5. **Async/await** - Non-blocking I/O throughout

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NOTION_API_KEY` | ✅ | - | Notion integration token (starts with `secret_`) |
| `MONGODB_URI` | ❌ | `mongodb://localhost:27017/notion-bot` | MongoDB connection string |
| `NOTION_API_VERSION` | ❌ | `2022-10-28` | Notion API version |
| `API_HOST` | ❌ | `0.0.0.0` | Server host |
| `API_PORT` | ❌ | `8000` | Server port |
| `DEBUG` | ❌ | `false` | Enable debug mode |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

## Notion Integration Setup

1. **Create Notion Integration:**
   - Go to https://www.notion.so/my-integrations
   - Click "Create new integration"
   - Give it a name and description
   - Copy the "Integration Token" (starts with `secret_`)

2. **Get Database ID:**
   - Open your Notion database
   - Copy the ID from the URL (32-character hex string)
   - Example: `https://notion.so/database/1a2b3c4d5e6f7890abcdef1234567890?v=...`

3. **Connect Integration to Database:**
   - In your Notion database, click "..."
   - Select "Connect to" → find your integration
   - Grant permissions

4. **Test Connection:**
   - Set environment variables
   - Run the API server
   - Test with the `/tasks/` endpoint

## Database Schema

### Workspaces Collection
```javascript
{
  "_id": ObjectId,
  "platform": "web|teams|slack",
  "platform_id": "channel_or_workspace_id", 
  "notion_database_id": "notion_database_uuid",
  "name": "Workspace Name",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### Indexes
- `{platform: 1, platform_id: 1}` (unique)

## Debugging Tips

### Common Issues

1. **MongoDB connection errors:**
   - Ensure `docker-compose up -d mongodb` is running
   - Check connection string format
   - Verify MongoDB credentials

2. **Notion API errors:**
   - Verify NOTION_API_KEY starts with `secret_`
   - Check database ID format (32 hex characters)
   - Ensure integration is connected to database

3. **Import errors:**
   - Activate virtual environment
   - Install all required packages
   - Check PYTHONPATH includes `src/`

### Debug Mode
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python src/main.py
```

### Test Database Access
```bash
# Check MongoDB connection
curl http://localhost:8000/health

# Test Notion database access
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","notion_database_id":"YOUR_DB_ID"}'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the code style (enforced by tools)
4. Add tests for new features
5. Update documentation
6. Submit Pull Request

### Code Style
- Use Black for formatting
- Follow isort import ordering
- Type hints required for all public APIs
- Write descriptive docstrings
- Keep functions focused and small

## Deployment

### Docker (Production)
```bash
# Build image
docker build -t notion-bot .

# Run with environment variables
docker run -d \
  --name notion-bot \
  -p 8000:8000 \
  -e NOTION_API_KEY=your_key_here \
  -e MONGODB_URI=mongodb://host/notion-bot \
  notion-bot
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export NOTION_API_KEY=your_key

# Run with production server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```
