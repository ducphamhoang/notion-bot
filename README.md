# Notion Bot API

Core task management APIs for Notion integration.

## Features

- ✅ Create tasks in Notion databases
- ✅ Workspace-to-Notion database mapping  
- ✅ MongoDB for metadata storage
- ✅ Rate limiting with exponential backoff
- ✅ Structured error handling
- ✅ Health checks and observability
- ✅ Unit and integration tests

## Architecture

This project follows a feature-first clean architecture approach with **Dependency Injection**:

```
src/
├── core/           # Shared infrastructure (database, Notion client, errors)
├── config/         # Configuration and environment management
├── features/       # Business features (tasks, workspaces, users)
│   ├── tasks/      # Task management feature
│   ├── workspaces/ # Workspace mapping feature
│   └── users/      # User mapping feature
└── adapters/       # Platform adapters (Teams, Slack, etc.)
```

### Key Architecture Principles

1. **Dependency Injection (DI)**: Services accept optional repository parameters for easy testing
2. **Clean Architecture**: Business logic independent of frameworks and databases
3. **Feature-First**: Code organized by business features, not technical layers
4. **Domain-Driven**: Custom exceptions and domain models for clear error handling

### Dependency Injection Pattern

All services follow this pattern for testability:

```python
class WorkspaceService:
    def __init__(self, repository: Optional[WorkspaceRepository] = None):
        """
        Service with optional repository injection.
        
        Args:
            repository: Optional repository for testing. 
                       Defaults to production repository if not provided.
        """
        self._repository = repository or WorkspaceRepository()
```

**Benefits**:
- ✅ Easy to test with mock repositories
- ✅ No monkey-patching required in tests
- ✅ Backward compatible (existing code works unchanged)
- ✅ Follows SOLID principles
- ✅ Uses FastAPI's native dependency override system

## Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Poetry (for dependency management)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ducphamhoang/notion-bot
cd notion-bot
```

2. Install dependencies:
```bash
poetry install
```

3. Start MongoDB:
```bash
docker-compose up -d mongodb
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Notion API credentials
```

5. Run the application:
```bash
poetry run python src/main.py
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGODB_URI` | Yes | MongoDB connection URI |
| `NOTION_API_KEY` | Yes | Notion integration token |
| `NOTION_API_VERSION` | No | Notion API version (default: 2022-10-28) |
| `API_HOST` | No | API server host (default: 0.0.0.0) |
| `API_PORT` | No | API server port (default: 8000) |
| `LOG_LEVEL` | No | Logging level (default: INFO) |

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

#### Tasks
- `POST /tasks/` - Create a new task
- Health check: `GET /tasks/health`

#### Workspaces  
- `POST /workspaces/` - Create workspace mapping
- `GET /workspaces/` - List all workspaces
- `GET /workspaces/query` - Query by platform

#### System
- `GET /` - API information
- `GET /health` - System health check

### Example: Create Task

```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix login bug",
    "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
    "assignee_id": "user_001", 
    "due_date": "2023-07-25T00:00:00.000Z",
    "priority": "High",
    "properties": {
      "Tags": {"multi_select": [{"name": "bug"}]}
    }
  }'
```

## Error Handling

The API uses standardized error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data", 
    "details": {
      "field": "title",
      "reason": "Required field missing"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Duplicate resource |
| `NOTION_API_ERROR` | 502 | Notion API failure |
| `RATE_LIMIT_EXCEEDED` | 503/429 | Rate limit hit |
| `INTERNAL_ERROR` | 500 | Unexpected error |

## Development

### Code Quality

This project uses several code quality tools:

- **Black**: Code formatting
- **isort**: Import sorting  
- **ruff**: Fast linting
- **mypy**: Type checking

Run all quality checks:
```bash
poetry run black src/
poetry run isort src/
poetry run ruff check src/
poetry run mypy src/
```

### Testing

Run all tests:
```bash
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test
poetry run pytest tests/unit/test_tasks_service.py::TestNotionTaskService::test_build_notion_properties_basic
```

### Monitoring & Observability

- **Structured JSON logging** with request IDs
- **Health check endpoint** monitoring dependencies
- **Performance metrics** (timing per endpoint)
- **Error tracking** with structured error codes

## Notion Integration Setup

1. Create a Notion account and workspace
2. Create an integration at https://www.notion.so/my-integrations
3. Copy the "Integration Token" (starts with `secret_`)
4. Add the integration to your database as a connection
5. Copy your database ID (32-character hex string from URL)

## Rate Limiting

Notion API has strict rate limits (3 requests/second). This API handles them automatically with:
- Exponential backoff (1s, 2s, 4s, 8s delays)
- Random jitter (±20%) to prevent synchronized retries  
- Graceful error responses when limits are exceeded

## Deployment

### Automated Deployment (Recommended)

The easiest way to deploy the application is using the automated deployment scripts:

**Linux/macOS:**
```bash
# 1. Make the script executable
chmod +x deploy.sh

# 2. Configure environment
cp .env.example .env
# Edit .env with your Notion API credentials

# 3. Deploy in development mode
./deploy.sh

# For production deployment
./deploy.sh -e prod
```

**Windows:**
```powershell
# 1. Configure environment
Copy-Item .env.example .env
# Edit .env with your Notion API credentials

# 2. Deploy in development mode
.\deploy.ps1

# For production deployment
.\deploy.ps1 -e prod
```

For more information about the deployment scripts, see [DEPLOYMENT_SCRIPTS.md](DEPLOYMENT_SCRIPTS.md).

### Development Deployment (Manual)

If you prefer to deploy manually:

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your Notion API credentials

# 2. Start MongoDB and the application
docker-compose up -d

# 3. Verify application is running
curl http://localhost:8000/health
```

**Alternative: Running without Docker Compose**

If Docker Compose fails due to validation errors or other issues:

```bash
# Start MongoDB with Docker
docker run -d --name notion-bot-mongodb -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password123 \
  -e MONGO_INITDB_DATABASE=notion-bot \
  mongo:7.0

# Install dependencies directly
pip install -r requirements.txt

# Run the application (set PYTHONPATH to allow module imports)
PYTHONPATH=. python -c "
import uvicorn
from src.main import app
from src.config.settings import get_settings

settings = get_settings()
print(f'Starting server on {settings.api_host}:{settings.api_port}')
uvicorn.run(app, host=settings.api_host, port=settings.api_port, reload=settings.debug, log_level='info')
"
```

### Production Deployment

#### Using Docker Compose

```bash
# For production deployment, use the production compose file
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

#### Using MongoDB Atlas (Recommended for Production)

1. Update your environment file:
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/notion-bot?retryWrites=true&w=majority
```

2. Deploy without MongoDB service:
```bash
# This will only start the app service, connecting to your Atlas instance
docker-compose -f docker-compose.prod.yml up -d app
```

### Common Deployment Issues & Solutions

1. **Docker Compose validation error**: If you see an error like `services.app.environment.NOTION_API_VERSION invalid jsonType time.Time`, use the automated deployment script or the manual Docker approach above.

2. **Module import errors**: If you see `ModuleNotFoundError: No module named 'src'`, run the application with the `PYTHONPATH=.` prefix.

3. **Application won't start**: Check that the `NOTION_API_KEY` in your `.env` file is valid and has appropriate permissions in Notion.

### Environment Security

- Never commit `.env` files
- Use secrets management in production
- Enable request logging for audit trails

### Performance Considerations

- Connection pooling for MongoDB and Notion
- Async/await throughout the stack
- Timeout configurations for external APIs
- Health checks with cached results

For more detailed deployment instructions including troubleshooting and common issues, see [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md).

For deployment best practices and verification, use the [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md).

## Contributing

1. Follow the existing code style (enforced by Black)
2. Add tests for new features
3. Update API documentation 
4. Ensure all tests pass before PR

## License

Add your license information here.
