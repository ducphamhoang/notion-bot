# Notion Bot API Documentation

## Overview

The Notion Bot API provides a centralized task management system integrated with Notion. It allows you to create, read, update, and delete tasks that are synchronized with Notion databases.

**Base URL**: `http://localhost:8000` (development) or your deployed URL  
**API Version**: 0.1.0

## Table of Contents

- [Authentication & Authorization](#authentication--authorization)
- [Rate Limiting](#rate-limiting)
- [Error Codes Reference](#error-codes-reference)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Metrics](#metrics)
  - [Tasks](#tasks)
  - [Workspaces](#workspaces)
  - [Users](#users)

---

## Authentication & Authorization

### Current Status (Phase 1)

**Authentication is NOT implemented in Phase 1.** The API is currently open and does not require authentication headers. This is suitable for development and testing purposes only.

### Future Implementation (Phase 2)

Phase 2 will implement authentication and authorization with the following features:

#### API Key Authentication

Each request will require an `X-API-Key` header:

```http
X-API-Key: your-api-key-here
```

#### OAuth 2.0 (For User Access)

For user-specific operations, OAuth 2.0 with JWT tokens will be supported:

```http
Authorization: Bearer <jwt-token>
```

#### Permission Model

- **Admin**: Full access to all resources
- **User**: Access to own tasks and workspaces they belong to
- **Read-Only**: View-only access to tasks

#### Security Best Practices

When authentication is implemented:

1. **Never expose API keys** in client-side code or public repositories
2. **Use HTTPS** in production environments
3. **Rotate keys regularly** (at least quarterly)
4. **Use environment variables** to store sensitive credentials
5. **Implement token expiration** (JWT tokens expire after 24 hours)

---

## Rate Limiting

### Notion API Rate Limits

The Notion Bot API is subject to Notion's API rate limits:

- **Rate Limit**: ~3 requests per second per integration
- **Burst Capacity**: Short bursts of up to 10 requests are tolerated
- **Retry Strategy**: Automatic exponential backoff with jitter

### API Rate Limiting Behavior

When a rate limit is hit:

1. **Automatic Retry**: The API automatically retries with exponential backoff
2. **Max Retries**: Up to 4 retries (5 total attempts)
3. **Backoff Strategy**: 
   - Initial delay: 1 second
   - Maximum delay: 8 seconds
   - Jitter: ±20% randomization to avoid thundering herd

### Rate Limit Headers

Future versions will include rate limit information in response headers:

```http
X-RateLimit-Limit: 180
X-RateLimit-Remaining: 150
X-RateLimit-Reset: 1699564800
```

### Rate Limit Error Response

When rate limit is exceeded after all retries:

```json
{
  "error": {
    "code": "RATE_LIMIT_ERROR",
    "message": "Notion API rate limit exceeded. Please try again later.",
    "details": {
      "retry_after": 60
    }
  }
}
```

### Best Practices

1. **Implement backoff** in your client code
2. **Cache responses** where possible to reduce API calls
3. **Batch operations** instead of making multiple sequential requests
4. **Monitor rate limit metrics** at `/metrics` endpoint

---

## Error Codes Reference

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource successfully created |
| 400 | Bad Request - Invalid request parameters |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Service temporarily unavailable |

### Application Error Codes

| Error Code | HTTP Status | Description | Solution |
|------------|-------------|-------------|----------|
| `VALIDATION_ERROR` | 400/422 | Request validation failed | Check request body against schema |
| `NOT_FOUND` | 404 | Resource not found | Verify resource ID exists |
| `DATABASE_ERROR` | 500 | Database operation failed | Check database connectivity |
| `NOTION_API_ERROR` | 500 | Notion API error | Check Notion API status and credentials |
| `RATE_LIMIT_ERROR` | 429 | Rate limit exceeded | Wait and retry with backoff |
| `SYNC_ERROR` | 500 | Task synchronization failed | Check Notion page/database exists |
| `DUPLICATE_ERROR` | 400 | Duplicate resource | Resource already exists |

### Error Response Format

All errors follow this standardized format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context",
      "validation_errors": [...]
    }
  }
}
```

### Examples

#### Validation Error

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "validation_errors": [
        {
          "field": "title",
          "message": "Title is required"
        },
        {
          "field": "status",
          "message": "Status must be one of: todo, in_progress, done"
        }
      ]
    }
  }
}
```

#### Not Found Error

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found",
    "details": {
      "task_id": "507f1f77bcf86cd799439011"
    }
  }
}
```

#### Notion API Error

```json
{
  "error": {
    "code": "NOTION_API_ERROR",
    "message": "Failed to sync task with Notion",
    "details": {
      "notion_error": "object_not_found",
      "notion_message": "Could not find database with ID: abc123"
    }
  }
}
```

---

## Endpoints

### Health Check

#### GET /health

Check the health status of the API and its dependencies.

**Response**: 200 OK (healthy) or 503 Service Unavailable (unhealthy)

```json
{
  "status": "healthy",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection is healthy"
    },
    "notion": {
      "status": "healthy",
      "notion_api": {
        "status": "connected",
        "api_version": "connected"
      }
    }
  }
}
```

**Health Check Caching**: Notion API connectivity is cached for 30 seconds to avoid excessive checks.

---

### Metrics

#### GET /metrics

Export Prometheus-compatible metrics for monitoring.

**Response**: 200 OK (text/plain)

**Metrics Exposed**:

- `http_request_duration_seconds` - Request duration percentiles (P50, P95, P99)
- `http_requests_total` - Total HTTP requests by endpoint and status code
- `notion_api_calls_total` - Total Notion API calls
- `rate_limit_hits_total` - Total rate limit hits

**Example**:

```
# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds summary
http_request_duration_seconds{endpoint="GET /tasks",quantile="0.5"} 0.123456
http_request_duration_seconds{endpoint="GET /tasks",quantile="0.95"} 0.456789
http_request_duration_seconds{endpoint="GET /tasks",quantile="0.99"} 0.789012

# HELP http_requests_total Total number of HTTP requests by endpoint and status code
# TYPE http_requests_total counter
http_requests_total{endpoint="GET /tasks",status_code="200"} 1500

# HELP notion_api_calls_total Total number of Notion API calls
# TYPE notion_api_calls_total counter
notion_api_calls_total 3500

# HELP rate_limit_hits_total Total number of rate limit hits
# TYPE rate_limit_hits_total counter
rate_limit_hits_total 12
```

---

### Tasks

For detailed task endpoint documentation, see the interactive API docs at `/docs` (in development mode).

**Key Endpoints**:

- `GET /tasks` - List all tasks with filtering and pagination
- `POST /tasks` - Create a new task
- `GET /tasks/{task_id}` - Get task by ID
- `PUT /tasks/{task_id}` - Update task
- `PATCH /tasks/{task_id}` - Partial update task
- `DELETE /tasks/{task_id}` - Delete task
- `POST /tasks/{task_id}/sync` - Sync task with Notion

---

### Workspaces

For detailed workspace endpoint documentation, see the interactive API docs at `/docs` (in development mode).

**Key Endpoints**:

- `GET /workspaces` - List all workspaces
- `POST /workspaces` - Create a new workspace
- `GET /workspaces/{workspace_id}` - Get workspace by ID
- `PUT /workspaces/{workspace_id}` - Update workspace
- `DELETE /workspaces/{workspace_id}` - Delete workspace

---

### Users

For detailed user endpoint documentation, see the interactive API docs at `/docs` (in development mode).

**Key Endpoints**:

- `GET /users` - List all users
- `POST /users` - Create a new user
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

---

## Interactive API Documentation

When running in development mode (`DEBUG=true`), the following interactive documentation is available:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These provide:
- Complete endpoint documentation
- Request/response schemas
- Try-it-out functionality
- Example requests and responses

---

## Support

For issues, questions, or feature requests:
1. Check the [Troubleshooting Guide](./OPERATIONS_RUNBOOK.md)
2. Review [Common Issues](./OPERATIONS_RUNBOOK.md#common-issues)
3. Contact the development team
