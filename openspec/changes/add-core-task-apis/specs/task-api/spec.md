# Task API Specification

## ADDED Requirements

### Requirement: Task Creation
The system SHALL provide an API endpoint to create tasks in a Notion database.

#### Scenario: Create task with required fields
- **WHEN** POST /tasks is called with `title` and `notion_database_id`
- **THEN** a new task is created in the specified Notion database
- **AND** the response includes `notion_task_id` and `notion_task_url`
- **AND** the response status is 201 Created

#### Scenario: Create task with optional fields
- **WHEN** POST /tasks includes `assignee_id`, `due_date`, and `priority`
- **THEN** the task is created with these properties set in Notion
- **AND** the assignee is resolved via user mapping table

#### Scenario: Create task with missing required fields
- **WHEN** POST /tasks is called without `title`
- **THEN** the response status is 400 Bad Request
- **AND** the error indicates which field is missing

#### Scenario: Create task with invalid database ID
- **WHEN** POST /tasks is called with non-existent `notion_database_id`
- **THEN** the response status is 404 Not Found
- **AND** the error message indicates database not found

#### Scenario: Notion API rate limit during creation
- **WHEN** POST /tasks triggers Notion rate limit (429 response)
- **THEN** the system retries with exponential backoff
- **AND** if retries succeed, returns 201 Created
- **AND** if all retries fail, returns 503 Service Unavailable

### Requirement: Task Retrieval
The system SHALL provide an API endpoint to retrieve tasks from Notion databases.

#### Scenario: List all tasks with defaults
- **WHEN** GET /tasks is called without parameters
- **THEN** returns first 20 tasks (default pagination)
- **AND** response includes `data`, `page`, `limit`, `total`, `has_more` fields
- **AND** response status is 200 OK

#### Scenario: Filter tasks by status
- **WHEN** GET /tasks is called with `?status=In Progress`
- **THEN** returns only tasks with matching status
- **AND** response follows pagination format

#### Scenario: Filter tasks by assignee
- **WHEN** GET /tasks is called with `?assignee=user_id_123`
- **THEN** returns only tasks assigned to the specified user
- **AND** user ID is mapped via users collection

#### Scenario: Filter tasks by date range
- **WHEN** GET /tasks is called with `?due_date_from=2025-01-01&due_date_to=2025-01-31`
- **THEN** returns only tasks with due dates in the specified range

#### Scenario: Sort tasks by due date
- **WHEN** GET /tasks is called with `?sort_by=due_date&order=asc`
- **THEN** returns tasks ordered by due date ascending
- **AND** tasks without due dates appear last

#### Scenario: Paginate task results
- **WHEN** GET /tasks is called with `?page=2&limit=10`
- **THEN** returns tasks 11-20
- **AND** `page` is 2 and `limit` is 10 in response

#### Scenario: Exceed pagination limit
- **WHEN** GET /tasks is called with `?limit=200`
- **THEN** the response status is 400 Bad Request
- **AND** error indicates maximum limit is 100

#### Scenario: Empty result set
- **WHEN** GET /tasks filters match no tasks
- **THEN** returns empty `data` array
- **AND** `total` is 0
- **AND** response status is 200 OK

### Requirement: Task Update
The system SHALL provide an API endpoint to update task properties.

#### Scenario: Update task status
- **WHEN** PATCH /tasks/{id} is called with `{"status": "Done"}`
- **THEN** the task status is updated in Notion
- **AND** response includes updated task data
- **AND** response status is 200 OK

#### Scenario: Update multiple fields
- **WHEN** PATCH /tasks/{id} includes multiple fields (status, assignee, priority)
- **THEN** all specified fields are updated
- **AND** unspecified fields remain unchanged

#### Scenario: Update non-existent task
- **WHEN** PATCH /tasks/{invalid_id} is called
- **THEN** response status is 404 Not Found
- **AND** error message indicates task not found

#### Scenario: Update with invalid field value
- **WHEN** PATCH /tasks/{id} includes invalid status value
- **THEN** response status is 400 Bad Request
- **AND** error indicates the validation failure

### Requirement: Task Deletion
The system SHALL provide an API endpoint to delete tasks.

#### Scenario: Delete existing task
- **WHEN** DELETE /tasks/{id} is called for valid task
- **THEN** the task is archived/deleted in Notion
- **AND** response status is 204 No Content

#### Scenario: Delete non-existent task
- **WHEN** DELETE /tasks/{invalid_id} is called
- **THEN** response status is 404 Not Found
- **AND** error message indicates task not found

### Requirement: Workspace Mapping
The system SHALL maintain mappings between chat platform channels and Notion databases.

#### Scenario: Store workspace mapping
- **WHEN** a workspace mapping is created with platform, platform_id, and notion_database_id
- **THEN** the mapping is stored in the workspaces collection
- **AND** future task operations can resolve the correct Notion database

#### Scenario: Retrieve workspace by platform ID
- **WHEN** querying for workspace by platform="teams" and platform_id="channel_123"
- **THEN** the corresponding Notion database ID is returned
- **AND** response includes workspace name and metadata

#### Scenario: Prevent duplicate workspace mappings
- **WHEN** creating a workspace mapping with duplicate platform+platform_id
- **THEN** the operation fails with 409 Conflict
- **AND** error message indicates duplicate mapping

### Requirement: User Mapping
The system SHALL maintain mappings between chat platform users and Notion users.

#### Scenario: Store user mapping
- **WHEN** a user mapping is created with platform_user_id and notion_user_id
- **THEN** the mapping is stored in the users collection
- **AND** future task operations can resolve assignees correctly

#### Scenario: Resolve platform user to Notion user
- **WHEN** creating a task with assignee referencing platform user ID
- **THEN** the system looks up the Notion user ID via users collection
- **AND** assigns the task to the corresponding Notion user

#### Scenario: Handle missing user mapping
- **WHEN** task operation references unmapped platform user
- **THEN** response status is 400 Bad Request
- **AND** error indicates user mapping not found

### Requirement: Error Handling
The system SHALL provide consistent error responses for all failure scenarios.

#### Scenario: Standardized error format
- **WHEN** any API error occurs
- **THEN** response follows standardized format with `error.code`, `error.message`, `error.details`
- **AND** HTTP status code matches error type

#### Scenario: Notion API failure
- **WHEN** Notion API returns 500 Internal Server Error
- **THEN** system returns 502 Bad Gateway
- **AND** error code is `NOTION_API_ERROR`
- **AND** error message is user-friendly (no raw Notion errors)

#### Scenario: Database connection failure
- **WHEN** MongoDB is unavailable during request
- **THEN** response status is 503 Service Unavailable
- **AND** error code is `DATABASE_UNAVAILABLE`

#### Scenario: Request timeout
- **WHEN** Notion API call exceeds timeout (10 seconds)
- **THEN** request is aborted
- **AND** response status is 504 Gateway Timeout

### Requirement: Performance
The system SHALL meet defined performance targets for API operations.

#### Scenario: Task creation response time
- **WHEN** POST /tasks is called under normal conditions
- **THEN** response is returned in less than 500ms (P95)

#### Scenario: Task listing response time
- **WHEN** GET /tasks is called with 20 results
- **THEN** response is returned in less than 500ms (P95)

#### Scenario: Handle concurrent requests
- **WHEN** 100 requests per second are made across all endpoints
- **THEN** all requests complete successfully
- **AND** no requests timeout or fail due to load

### Requirement: API Documentation
The system SHALL provide OpenAPI/Swagger documentation for all endpoints.

#### Scenario: Access API documentation
- **WHEN** navigating to /docs or /api-docs endpoint
- **THEN** interactive Swagger UI is displayed
- **AND** all endpoints are documented with parameters and examples

#### Scenario: Try API calls from documentation
- **WHEN** using Swagger UI "Try it out" feature
- **THEN** API calls execute successfully
- **AND** responses are displayed in the UI
