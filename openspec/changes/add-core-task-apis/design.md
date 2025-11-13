# Design: Core Task APIs and Database

## Context
This is the foundational layer of the Notion bot system. It establishes the data persistence strategy, external API integration patterns, and core REST API that all other components will depend on. This design must support future extensions including webhook handlers, rule engine, and AI agent integration.

**Constraints:**
- Notion API rate limits (3 requests per second per integration)
- MongoDB as the chosen database (Docker local, Atlas production)
- Must support multiple workspaces/databases per installation
- Performance target: < 500ms API response time

**Stakeholders:**
- Frontend developers (Web Chat UI)
- Platform integration developers (Teams, Slack adapters)
- Future AI agent developers

## Goals / Non-Goals

**Goals:**
- Provide reliable CRUD operations for Notion tasks via REST API
- Handle Notion API rate limits gracefully
- Support workspace and user ID mapping between platforms and Notion
- Enable filtering, sorting, and pagination for task queries
- Establish patterns for error handling and logging
- Ensure data validation at API boundaries

**Non-Goals:**
- Real-time notifications (handled by Rule Engine in later phase)
- Natural language processing (delegated to AI agents in later phase)
- Multi-tenancy with strict isolation (single deployment per organization for MVP)
- Caching with Redis (optimization for Phase 3)

## Decisions

### Decision 1: Three-Layer Architecture
**What:** Separate API, Service, and Data layers
- **API Layer:** FastAPI routes, request/response handling, validation
- **Service Layer:** Business logic, Notion SDK calls, error handling
- **Data Layer:** MongoDB models, queries, and connection management

**Why:** Clear separation enables testing, allows service layer reuse by webhooks and agents, and makes it easy to swap implementations.

**Alternatives considered:**
- Single-layer with routes calling Notion directly: Too tightly coupled, hard to test
- Four-layer with additional repository pattern: Over-engineering for MVP scale

### Decision 2: MongoDB Collections Schema
**What:** Two primary collections:
```json
// workspaces collection
{
  "_id": "ObjectId",
  "platform": "teams|slack|discord",
  "platform_id": "channel_or_workspace_id",
  "notion_database_id": "notion_db_uuid",
  "name": "Human-readable name",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}

// users collection
{
  "_id": "ObjectId",
  "platform": "teams|slack|discord",
  "platform_user_id": "user_id_on_platform",
  "notion_user_id": "notion_user_uuid",
  "display_name": "User Display Name",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

**Why:**
- Simple flat structure for MVP
- Supports multi-platform mapping via platform discriminator
- Denormalized for read performance (no joins needed)

**Indexes:**
- `workspaces`: `{platform: 1, platform_id: 1}` (unique)
- `users`: `{platform: 1, platform_user_id: 1}` (unique)

### Decision 3: Rate Limit Handling Strategy
**What:** Implement exponential backoff with jitter
- Detect 429 responses from Notion API
- Retry with delays: 1s, 2s, 4s, 8s (max 4 retries)
- Add random jitter (±20%) to prevent thundering herd
- Return 503 Service Unavailable if all retries exhausted

**Why:** Notion API has strict rate limits. Naive retry causes cascading failures.

**Alternatives considered:**
- Queue all Notion requests: Too complex for MVP, adds Redis dependency
- Fail immediately: Poor user experience
- Fixed delay retry: Can cause synchronized retry storms

### Decision 4: Error Response Format
**What:** Standardized error response:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": {
      "field": "title",
      "reason": "Required field missing"
    }
  }
}
```

**Why:** Consistent error handling across all clients and platform adapters.

**Error codes:**
- `VALIDATION_ERROR`: 400 - Invalid request data
- `NOT_FOUND`: 404 - Task/workspace not found
- `NOTION_API_ERROR`: 502 - Notion API failure
- `RATE_LIMIT_EXCEEDED`: 503 - Rate limit hit after retries
- `INTERNAL_ERROR`: 500 - Unexpected errors

### Decision 5: Pagination Strategy
**What:** Offset-based pagination for MVP
- Query params: `page` (default: 1), `limit` (default: 20, max: 100)
- Response includes: `data[]`, `page`, `limit`, `total`, `has_more`

**Why:** Simple to implement, adequate for expected data volumes (< 10k tasks per database).

**Alternatives considered:**
- Cursor-based: Better for large datasets, but adds complexity
- No pagination: Unacceptable for production

### Decision 6: Notion Property Mapping
**What:** Map standard task properties to Notion page properties:
- `title` → Title property
- `status` → Select/Status property (configurable name)
- `assignee_id` → Person property (requires user mapping)
- `due_date` → Date property
- `priority` → Select property
- `properties` → Additional custom properties (passthrough)

**Why:** Flexible schema allows different Notion database templates while maintaining core fields.

**Constraint:** Workspace configuration must specify property name mappings.

## Risks / Trade-offs

### Risk 1: Notion API Changes
**Risk:** Notion changes API schema or behavior
**Mitigation:**
- Use official SDK (handles many changes transparently)
- Version lock SDK in production
- Monitor Notion changelog and deprecation notices

### Risk 2: Database Connection Failures
**Risk:** MongoDB unavailable during requests
**Mitigation:**
- Connection pooling with auto-reconnect
- Health check endpoint (`GET /health`)
- Graceful degradation: Return cached data if available (future Redis integration)

### Risk 3: Slow Notion API Responses
**Risk:** Notion API latency causes timeout
**Mitigation:**
- Set reasonable timeouts (10s for API calls)
- Implement async processing for bulk operations (future)
- Monitor P95/P99 latencies

### Trade-off: No Caching in MVP
**Decision:** Skip Redis caching for MVP
**Impact:** Higher Notion API usage, potential rate limit hits
**Justification:** Reduces complexity, allows learning usage patterns before optimizing

## Migration Plan

**Phase 1 (Current):** Bootstrap
1. Deploy MongoDB container
2. Create database and collections
3. Deploy API service
4. Smoke test with curl/Postman

**Phase 2:** Add clients
1. Web Chat UI integration
2. Teams adapter integration
3. Monitor error rates and latencies

**Phase 3:** Optimization
1. Add Redis caching if Notion API limits are hit
2. Implement request queuing if needed
3. Scale horizontally if load exceeds single instance

**Rollback:**
- If critical issues arise, disable API endpoints via feature flag
- Clients fall back to direct Notion access (manual)

## Open Questions

1. **Q:** Should we support multiple Notion integrations (different workspaces) per deployment?
   **A:** Yes, but scope to single workspace for MVP. Design supports multiple via workspace table.

2. **Q:** How to handle Notion database schema validation (ensure required properties exist)?
   **A:** Add configuration validation step: On workspace setup, query database schema and validate required properties exist.

3. **Q:** Should task GET endpoint return full Notion page properties or filtered subset?
   **A:** Filtered subset for MVP (title, status, assignee, due_date, priority). Add `?include=all` flag for full response.

4. **Q:** Authentication/authorization for API endpoints?
   **A:** Deferred to Phase 2 (OAuth implementation). For MVP, use hardcoded API key in environment.
