# Implementation Tasks

> **Architecture Approach:** Feature-first vertical slicing. Each feature is implemented end-to-end (database → service → API → tests) before moving to the next feature. This enables incremental delivery and faster feedback loops.

---

## 0. Foundation & Project Setup

### 0.1 Initialize project structure
- [x] Create project directory structure following clean architecture
  - `src/features/` - Feature modules
  - `src/core/` - Shared infrastructure
  - `src/config/` - Configuration
  - `tests/` - Test files mirroring src structure
- [x] Set up FastAPI or Express project with dependency injection support
- [x] Configure linting (Black/Pylint for Python, ESLint/Prettier for JS)
- **Acceptance:** Project runs with `--help` command showing version ✅

### 0.2 Setup development database
- [x] Create `docker-compose.yml` with MongoDB service
- [x] Create `src/core/database/connection.py|ts` with connection pooling
- [x] Add retry logic for connection failures (3 retries with backoff)
- [x] Create health check function to verify MongoDB connectivity
- **Acceptance:** `docker-compose up` starts MongoDB; health check passes ✅

### 0.3 Configure environment and secrets
- [x] Create `.env.example` with required variables:
  - `MONGODB_URI`, `NOTION_API_KEY`, `NOTION_API_VERSION`, `CORS_ORIGINS`
- [x] Create `src/config/settings.py|ts` using Pydantic Settings or dotenv
- [x] Add validation to fail fast on missing required config
- **Acceptance:** App fails with clear error if `NOTION_API_KEY` missing ✅

### 0.4 Setup Notion SDK client
- [x] Install Notion SDK (`notion-sdk-py` or `@notionhq/client`)
- [x] Create `src/core/notion/client.py|ts` with initialized client
- [x] Add request timeout configuration (10 seconds)
- [x] Test connection with simple API call (list databases)
- **Acceptance:** Can query Notion API successfully; timeout enforced ✅

---

## 1. Feature: Create Task

> **Goal:** Enable API clients to create tasks in Notion databases
> **Dependencies:** Foundation (0.x)

### 1.1 Database layer for workspace mapping
- [x] Create `src/features/workspaces/models.py|ts` with Workspace schema:
  ```python
  {
    "_id": ObjectId,
    "platform": str,           # teams|slack|web
    "platform_id": str,         # channel or workspace ID
    "notion_database_id": str,  # UUID
    "name": str,
    "property_mappings": dict,  # NEW: Custom property name mappings
    "created_at": datetime,
    "updated_at": datetime
  }
  ```
- [x] Create index: `{platform: 1, platform_id: 1}` (unique)
- [x] Create `src/features/workspaces/repository.py|ts` with:
  - `find_by_platform_id(platform, platform_id) -> Workspace`
  - `create(workspace_data) -> Workspace`
- **Acceptance:** Can insert workspace and query by platform_id ✅

### 1.2 Create task request/response models
- [x] Create `src/features/tasks/dto/create_task_request.py|ts`:
  - Required: `title: str`, `notion_database_id: str`
  - Optional: `assignee_id: str`, `due_date: datetime`, `priority: str`, `properties: dict`
- [x] Add Pydantic/class-validator validation rules
- [x] Create `src/features/tasks/dto/create_task_response.py|ts`:
  - `notion_task_id: str`, `notion_task_url: str`, `created_at: datetime`
- **Acceptance:** Invalid request (missing title) fails validation with clear error ✅

### 1.3 Implement Notion create task service
- [x] Create `src/features/tasks/services/notion_task_service.py|ts`
- [x] Implement `create_task(request: CreateTaskRequest) -> CreateTaskResponse`:
  - Map request fields to Notion page properties
  - Call Notion SDK `pages.create()`
  - Handle Notion API errors and map to domain errors
  - Return response with task ID and URL
- **Acceptance:** Successfully creates task in Notion; verify in Notion UI ✅

### 1.4 Add rate limit handling to create task
- [x] Create `src/core/notion/rate_limiter.py|ts` with exponential backoff
- [x] Implement retry logic: 1s, 2s, 4s, 8s delays (max 4 retries)
- [x] Add random jitter (±20%) to delays
- [x] Detect 429 status and trigger retry; fail with RateLimitError after exhaustion
- **Acceptance:** Mock 429 response triggers retries; success after retry works ✅

### 1.5 Implement POST /tasks API endpoint
- [x] Create `src/features/tasks/routes.py|ts` with POST `/tasks` handler
- [x] Inject NotionTaskService via dependency injection
- [x] Validate request body using Pydantic/validators
- [x] Call service layer and return 201 Created with response
- [x] Add error handling middleware to catch validation and service errors
- **Acceptance:** `curl -X POST /tasks -d '{"title":"Test","notion_database_id":"xxx"}'` returns 201 ✅

### 1.6 Write tests for create task feature
- [x] Unit test: Request validation (missing title, invalid database ID format)
- [x] Unit test: NotionTaskService maps request to Notion properties correctly
- [x] Integration test: End-to-end POST /tasks creates task in test Notion database
- [x] Integration test: Rate limit retry behavior with mocked 429 responses
- [x] Integration test: Error handling (404 database not found, 400 bad request)
- **Acceptance:** All tests pass; coverage >80% for create task feature ✅

### 1.7 Document create task endpoint
- [x] Add OpenAPI schema annotation to POST /tasks route
- [x] Write example request/response in docstring or API docs
- [x] Add to API documentation page with curl example
- **Acceptance:** Swagger UI shows POST /tasks with request/response examples ✅

---

## 2. Feature: List & Filter Tasks

> **Goal:** Enable querying tasks with filters, sorting, and pagination
> **Dependencies:** Feature 1 (Create Task)

### 2.1 Create list tasks request/response models
- [ ] Create `src/features/tasks/dto/list_tasks_request.py|ts`:
  - Optional filters: `status: str`, `assignee: str`, `due_date_from: datetime`, `due_date_to: datetime`, `project_id: str`
  - Pagination: `page: int = 1`, `limit: int = 20`
  - Sorting: `sort_by: str`, `order: asc|desc`
- [ ] Add validation: `limit` max 100, `page` >= 1
- [ ] Create `src/features/tasks/dto/list_tasks_response.py|ts`:
  - `data: List[TaskSummary]`, `page: int`, `limit: int`, `total: int`, `has_more: bool`
- **Acceptance:** Invalid pagination (page=0) fails validation

### 2.2 Implement Notion query tasks service
- [ ] Add `list_tasks(request: ListTasksRequest) -> ListTasksResponse` to NotionTaskService
- [ ] Build Notion API filter object from request filters
- [ ] Apply sorting using Notion sorts parameter
- [ ] Implement offset-based pagination using `start_cursor`
- [ ] Map Notion pages to TaskSummary DTOs
- **Acceptance:** Query with status filter returns only matching tasks from Notion

### 2.3 Implement GET /tasks API endpoint
- [ ] Add GET `/tasks` handler in `src/features/tasks/routes.py|ts`
- [ ] Parse query parameters into ListTasksRequest
- [ ] Call NotionTaskService.list_tasks()
- [ ] Return 200 OK with paginated response
- **Acceptance:** `curl "/tasks?status=Done&page=1&limit=10"` returns filtered results

### 2.4 Add multi-filter and sorting support
- [ ] Test combining multiple filters (status + assignee + date range)
- [ ] Implement sort by due_date, created_time, priority
- [ ] Handle tasks with null/missing sort fields (appear last)
- **Acceptance:** `curl "/tasks?status=Open&sort_by=due_date&order=asc"` returns sorted results

### 2.5 Write tests for list tasks feature
- [ ] Unit test: Filter builder creates correct Notion query
- [ ] Unit test: Pagination calculates offset correctly
- [ ] Integration test: GET /tasks with no filters returns all tasks
- [ ] Integration test: Status filter returns matching subset
- [ ] Integration test: Date range filter works correctly
- [ ] Integration test: Pagination returns correct pages
- [ ] Integration test: Exceeding limit (>100) returns 400 error
- **Acceptance:** All tests pass; edge cases covered

### 2.6 Document list tasks endpoint
- [ ] Add OpenAPI schema with query parameter definitions
- [ ] Document filter options and valid values
- [ ] Add pagination example showing `has_more` usage
- **Acceptance:** Swagger UI shows all query params with descriptions

---

## 3. Feature: Update Task

> **Goal:** Enable updating task properties (status, assignee, priority, etc.)
> **Dependencies:** Feature 2 (List Tasks - for verification)

### 3.1 Create update task request model
- [ ] Create `src/features/tasks/dto/update_task_request.py|ts`:
  - All fields optional: `status`, `assignee_id`, `due_date`, `priority`, `properties`
  - Validate at least one field must be provided
- [ ] Create `src/features/tasks/dto/update_task_response.py|ts` with updated task data
- **Acceptance:** Empty update request fails validation

### 3.2 Implement Notion update task service
- [ ] Add `update_task(task_id: str, request: UpdateTaskRequest) -> UpdateTaskResponse` to NotionTaskService
- [ ] Call Notion SDK `pages.update()`
- [ ] Only include provided fields in update (partial update)
- [ ] Handle 404 if task not found in Notion
- **Acceptance:** Update status in Notion; verify change in Notion UI

### 3.3 Implement PATCH /tasks/{id} endpoint
- [ ] Add PATCH `/tasks/{id}` handler in routes
- [ ] Validate task_id format (UUID)
- [ ] Call update service and return 200 OK with updated task
- [ ] Return 404 if task doesn't exist
- **Acceptance:** `curl -X PATCH /tasks/{id} -d '{"status":"Done"}'` updates task

### 3.4 Write tests for update task feature
- [ ] Unit test: Partial update includes only provided fields
- [ ] Integration test: Update single field (status)
- [ ] Integration test: Update multiple fields
- [ ] Integration test: Update non-existent task returns 404
- [ ] Integration test: Invalid field value returns 400
- **Acceptance:** All tests pass

### 3.5 Document update task endpoint
- [ ] Add OpenAPI schema for PATCH /tasks/{id}
- [ ] Document which fields are updateable
- [ ] Add example showing partial update
- **Acceptance:** Swagger UI shows PATCH endpoint with examples

---

## 4. Feature: Delete Task

> **Goal:** Enable deleting/archiving tasks
> **Dependencies:** Feature 2 (List Tasks - for verification)

### 4.1 Implement Notion delete task service
- [ ] Add `delete_task(task_id: str) -> None` to NotionTaskService
- [ ] Call Notion SDK `pages.update()` with `archived: true`
- [ ] Handle 404 if task not found
- **Acceptance:** Delete task; verify archived in Notion

### 4.2 Implement DELETE /tasks/{id} endpoint
- [ ] Add DELETE `/tasks/{id}` handler in routes
- [ ] Call delete service and return 204 No Content on success
- [ ] Return 404 if task doesn't exist
- **Acceptance:** `curl -X DELETE /tasks/{id}` archives task

### 4.3 Write tests for delete task feature
- [ ] Integration test: Delete existing task returns 204
- [ ] Integration test: Delete non-existent task returns 404
- [ ] Integration test: Deleted task doesn't appear in GET /tasks
- **Acceptance:** All tests pass

### 4.4 Document delete task endpoint
- [ ] Add OpenAPI schema for DELETE /tasks/{id}
- [ ] Note that deletion is actually archiving in Notion
- **Acceptance:** Swagger UI documents DELETE endpoint

---

## 5. Feature: Workspace Management

> **Goal:** Enable configuration of workspace-to-database mappings
> **Dependencies:** Foundation (workspace repository from 1.1)

### 5.1 Create workspace configuration models
- [ ] Enhance Workspace model from 1.1 if needed
- [ ] Create `src/features/workspaces/dto/create_workspace_request.py|ts`:
  - `platform: str`, `platform_id: str`, `notion_database_id: str`, `name: str`
- [ ] Create `src/features/workspaces/dto/workspace_response.py|ts`
- **Acceptance:** Models validated correctly

### 5.2 Implement workspace service
- [ ] Create `src/features/workspaces/services/workspace_service.py|ts`
- [ ] Implement `create_workspace(request) -> WorkspaceResponse`
- [ ] Implement `get_workspace_by_platform(platform, platform_id) -> WorkspaceResponse`
- [ ] Handle duplicate workspace creation (409 Conflict)
- [ ] Validate Notion database exists by querying Notion API
- **Acceptance:** Can create and retrieve workspace mapping

### 5.3 Implement workspace API endpoints
- [ ] Add POST `/workspaces` to create workspace mapping
- [ ] Add GET `/workspaces?platform={p}&platform_id={id}` to retrieve mapping
- [ ] Add GET `/workspaces` to list all workspaces
- **Acceptance:** Can configure workspace via API

### 5.4 Write tests for workspace feature
- [ ] Integration test: Create workspace mapping succeeds
- [ ] Integration test: Duplicate workspace returns 409
- [ ] Integration test: Query by platform_id returns correct workspace
- [ ] Integration test: Invalid Notion database ID fails validation
- **Acceptance:** All tests pass

### 5.5 Document workspace endpoints
- [ ] Add OpenAPI schemas for workspace endpoints
- [ ] Document workspace configuration flow
- **Acceptance:** Swagger UI shows workspace endpoints

---

## 6. Feature: User Mapping

> **Goal:** Map platform users to Notion users for assignee resolution
> **Dependencies:** Foundation

### 6.1 Create user mapping models
- [ ] Create `src/features/users/models.py|ts` with User schema (from 0.x):
  ```python
  {
    "_id": ObjectId,
    "platform": str,
    "platform_user_id": str,
    "notion_user_id": str,
    "display_name": str,
    "created_at": datetime,
    "updated_at": datetime
  }
  ```
- [ ] Create index: `{platform: 1, platform_user_id: 1}` (unique)
- [ ] Create `src/features/users/repository.py|ts` with CRUD operations
- **Acceptance:** Can store and query user mappings

### 6.2 Create user mapping DTOs
- [ ] Create `src/features/users/dto/create_user_mapping_request.py|ts`
- [ ] Create `src/features/users/dto/user_mapping_response.py|ts`
- **Acceptance:** DTOs validate correctly

### 6.3 Implement user mapping service
- [ ] Create `src/features/users/services/user_mapping_service.py|ts`
- [ ] Implement `create_mapping(request) -> UserMappingResponse`
- [ ] Implement `resolve_notion_user_id(platform, platform_user_id) -> str`
- [ ] Handle missing mapping gracefully (return clear error)
- **Acceptance:** Can create mapping and resolve user IDs

### 6.4 Integrate user mapping with task creation
- [ ] Modify NotionTaskService.create_task to resolve assignee_id via user mapping
- [ ] If assignee_id provided but no mapping exists, return 400 with clear error
- **Acceptance:** Create task with assignee uses mapped Notion user ID

### 6.5 Implement user mapping API endpoints
- [ ] Add POST `/users/mappings` to create mapping
- [ ] Add GET `/users/mappings?platform={p}&platform_user_id={id}` to query
- [ ] Add GET `/users/mappings` to list all mappings
- **Acceptance:** Can manage user mappings via API

### 6.6 Write tests for user mapping feature
- [ ] Integration test: Create user mapping succeeds
- [ ] Integration test: Resolve Notion user ID works
- [ ] Integration test: Task creation with valid assignee mapping works
- [ ] Integration test: Task creation with missing assignee mapping returns 400
- **Acceptance:** All tests pass

### 6.7 Document user mapping endpoints
- [ ] Add OpenAPI schemas
- [ ] Document user mapping configuration flow
- **Acceptance:** Swagger UI shows user mapping endpoints

---

## 7. Cross-Cutting: Error Handling & Observability

> **Goal:** Standardize error responses and add observability
> **Dependencies:** All features (refactoring)

### 7.1 Implement standardized error responses
- [x] Create `src/core/errors/error_handler.py|ts` middleware
- [x] Define error response schema:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable message",
      "details": {}
    }
  }
  ```
- [x] Map common exceptions to error codes:
  - `ValidationError` → 400 `VALIDATION_ERROR`
  - `NotFoundError` → 404 `NOT_FOUND`
  - `NotionAPIError` → 502 `NOTION_API_ERROR`
  - `RateLimitError` → 503 `RATE_LIMIT_EXCEEDED`
- [x] Add global exception handler to FastAPI/Express
- **Acceptance:** All endpoints return standardized error format ✅

### 7.2 Add structured logging
- [x] Configure JSON structured logging (use `structlog` or `winston`)
- [x] Add request ID middleware (generate UUID per request)
- [x] Log all API requests with: method, path, status, duration, request_id
- [x] Log service layer operations with context (task_id, workspace_id, etc.)
- [x] Never log sensitive data (tokens, passwords)
- **Acceptance:** All requests logged in JSON format with request_id ✅

### 7.3 Add health check endpoint
- [x] Implement GET `/health` endpoint
- [x] Check MongoDB connection health
- [ ] Check Notion API connectivity (cached, refresh every 30s)
- [x] Return 200 OK if healthy, 503 if unhealthy with details
- **Acceptance:** `/health` returns status of dependencies ⚠️ (Notion check pending)

### 7.4 Add metrics and monitoring hooks
- [ ] Add middleware to track request duration (P50, P95, P99)
- [ ] Add counter for HTTP status codes by endpoint
- [ ] Add counter for Notion API calls and rate limit hits
- [ ] Expose metrics endpoint (Prometheus format if applicable)
- **Acceptance:** Metrics endpoint shows request counts and latencies ❌ (Not implemented)

### 7.5 Write tests for error handling
- [x] Test validation error returns correct format
- [x] Test 404 error returns correct format
- [x] Test Notion API error mapped correctly
- [x] Test health check with healthy/unhealthy database
- **Acceptance:** All error scenarios covered ✅

---

## 8. Documentation & Deployment Readiness

> **Goal:** Finalize documentation and prepare for deployment
> **Dependencies:** All features

### 8.1 Complete API documentation
- [x] Ensure all endpoints have OpenAPI annotations (for POST /tasks)
- [ ] Add authentication/authorization section (even if deferred to Phase 2)
- [ ] Add rate limiting documentation
- [ ] Add error codes reference table
- **Acceptance:** Swagger UI fully documents all endpoints ⚠️ (Partial - only POST /tasks)

### 8.2 Write deployment guide
- [x] Document environment variables and their purposes (see .env.example)
- [x] Document MongoDB setup (Docker Compose for local, Atlas for prod)
- [ ] Document Notion integration setup (creating integration, getting API key)
- [ ] Add step-by-step deployment instructions
- **Acceptance:** New developer can run system following guide ⚠️ (Partial)

### 8.3 Write runbook for operations
- [ ] Document common issues and troubleshooting steps
- [ ] Document how to monitor system health
- [ ] Document backup and recovery procedures for MongoDB
- [ ] Document how to handle Notion API rate limits
- **Acceptance:** Operations team has runbook ❌

### 8.4 Performance testing
- [ ] Load test GET /tasks endpoint (100 req/s for 1 minute)
- [ ] Verify P95 latency < 500ms
- [ ] Test concurrent task creation (50 simultaneous requests)
- [ ] Verify no errors under load
- **Acceptance:** Performance targets met ❌

### 8.5 Security review
- [x] Review code for SQL/NoSQL injection vulnerabilities
- [x] Ensure secrets not hardcoded or logged
- [x] Verify input validation on all endpoints (POST /tasks)
- [x] Test error messages don't leak sensitive info
- **Acceptance:** No security issues found ✅ (for implemented features)

---

## Task Summary by Feature

- **Foundation:** 4 tasks ✅ **COMPLETED**
- **Feature 1 (Create Task):** 7 tasks ✅ **COMPLETED**
- **Feature 2 (List Tasks):** 6 tasks ❌ **NOT STARTED**
- **Feature 3 (Update Task):** 5 tasks ❌ **NOT STARTED**
- **Feature 4 (Delete Task):** 4 tasks ❌ **NOT STARTED**
- **Feature 5 (Workspace Management):** 5 tasks ⚠️ **PARTIAL** (models done, routes/service TBD)
- **Feature 6 (User Mapping):** 7 tasks ❌ **NOT STARTED**
- **Cross-Cutting:** 5 tasks ⚠️ **MOSTLY DONE** (4/5 complete, metrics pending)
- **Documentation & Deployment:** 5 tasks ⚠️ **PARTIAL** (2/5 complete)

**Total: 48 tasks**
**Completed: ~20 tasks (42%)**
**Remaining: ~28 tasks (58%)**

---

## 📊 Current Completion Status

| Section | Status | Progress |
|---------|--------|----------|
| 0. Foundation | ✅ Complete | 4/4 (100%) |
| 1. Create Task | ✅ Complete | 7/7 (100%) |
| 2. List Tasks | ❌ Not Started | 0/6 (0%) |
| 3. Update Task | ❌ Not Started | 0/5 (0%) |
| 4. Delete Task | ❌ Not Started | 0/4 (0%) |
| 5. Workspace Mgmt | ⚠️ Partial | 2/5 (40%) |
| 6. User Mapping | ❌ Not Started | 0/7 (0%) |
| 7. Cross-Cutting | ⚠️ Mostly Done | 4/5 (80%) |
| 8. Documentation | ⚠️ Partial | 2/5 (40%) |
| **TOTAL** | **In Progress** | **~19/48 (40%)** |

---

## 🎯 Next Priority Features

To complete the MVP, implement features in this order:

1. **Feature 2: List & Filter Tasks** (6 tasks) - High Priority
2. **Feature 3: Update Task** (5 tasks) - High Priority
3. **Feature 4: Delete Task** (4 tasks) - High Priority
4. **Feature 6: User Mapping** (7 tasks) - Medium Priority
5. **Complete Workspace Management** (3 remaining tasks) - Medium Priority
6. **Add Metrics** (1 task from Cross-Cutting) - Low Priority
7. **Finalize Documentation** (3 remaining tasks) - Before Production
