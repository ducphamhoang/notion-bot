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

This project follows a feature-first clean architecture approach:

```
src/
├── core/           # Shared infrastructure (database, Notion client, errors)
├── config/         # Configuration and environment management
├── features/       # Business features (tasks, workspaces, users)
│   ├── tasks/      # Task management feature
│   └── workspaces/ # Workspace mapping feature
└── adapters/       # Platform adapters (Teams, Slack, etc.)
```

## Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Poetry (for dependency management)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
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

## Production Deployment

### MongoDB Setup

- **Development**: Docker Compose (as shown)
- **Production**: MongoDB Atlas recommended

### Environment Security

- Never commit `.env` files
- Use secrets management in production
- Enable request logging for audit trails

### Performance Considerations

- Connection pooling for MongoDB and Notion
- Async/await throughout the stack
- Timeout configurations for external APIs
- Health checks with cached results

## Contributing

1. Follow the existing code style (enforced by Black)
2. Add tests for new features
3. Update API documentation 
4. Ensure all tests pass before PR

## License

Add your license information here.
