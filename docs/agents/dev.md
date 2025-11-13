# Hướng dẫn Phát triển & Kiến trúc (dev.md)

## 1. Lời mở đầu

Tài liệu này định nghĩa các quy tắc, "best practice" và kiến trúc phần mềm được áp dụng cho dự án Notion Bot. Mục tiêu là để đảm bảo code được viết ra có chất lượng cao, nhất quán, dễ đọc, dễ bảo trì và mở rộng.

**Tất cả các lập trình viên và AI agent tham gia vào dự án này BẮT BUỘC phải tuân thủ các hướng dẫn dưới đây.**

---

## 2. Tech Stack & Code Quality Tools

### Python Stack

#### a. Formatting: `Black` & `isort`
- **Black:** Tự động định dạng code. Mọi tranh cãi về style (dấu nháy đơn/kép, xuống dòng,...) sẽ được loại bỏ.
- **isort:** Tự động sắp xếp các câu lệnh `import` một cách gọn gàng, chuẩn mực.

#### b. Linting: `Ruff`
- **Ruff:** Một linter cực nhanh viết bằng Rust. Nó sẽ giúp phát hiện các lỗi tiềm ẩn, code không dùng đến, và các pattern code xấu. Ruff tích hợp sẵn chức năng của `flake8`, `isort` và nhiều plugin khác.

#### c. Type Hinting: `mypy`
- **Bắt buộc** sử dụng Type Hint cho tất cả các hàm, phương thức và biến quan trọng.
- Sử dụng `mypy` để kiểm tra tĩnh (static type checking), đảm bảo không có lỗi về kiểu dữ liệu trước khi chạy code.
- **Ví dụ:**
  ```python
  def create_task(title: str, user_id: int | None = None) -> CreateTaskResponse:
      # function body
      ...
  ```

#### d. Dependency Management: `Poetry`
- Dự án sẽ sử dụng `Poetry` để quản lý các thư viện phụ thuộc.
- Mọi thư viện phải được thêm vào file `pyproject.toml` thông qua lệnh `poetry add <library_name>`.

### Node.js/TypeScript Stack (Alternative)

Nếu sử dụng Node.js:
- **Linting:** ESLint với cấu hình TypeScript
- **Formatting:** Prettier
- **Type Checking:** TypeScript compiler (`tsc`)
- **Package Management:** npm hoặc yarn
- **Validation:** class-validator hoặc Zod

### Naming Conventions (Áp dụng cho cả Python và TypeScript)

#### Python:
- `snake_case` cho biến, hàm, phương thức, và module (e.g., `def create_task(...)`).
- `PascalCase` cho class (e.g., `class TaskService`, `class CreateTaskRequest`).
- Hằng số: `ALL_CAPS` (e.g., `API_TIMEOUT = 30`).
- File names: `snake_case.py` (e.g., `notion_task_service.py`)

#### TypeScript/JavaScript:
- `camelCase` cho biến, hàm, phương thức (e.g., `function createTask(...)`)
- `PascalCase` cho class, interface, type (e.g., `class TaskService`, `interface CreateTaskRequest`)
- Hằng số: `ALL_CAPS` (e.g., `const API_TIMEOUT = 30`)
- File names: `kebab-case.ts` hoặc `camelCase.ts` (e.g., `notion-task-service.ts` hoặc `notionTaskService.ts`)

---

## 3. Kiến trúc "Feature-First Clean Architecture"

Để dự án dễ dàng mở rộng, chúng ta sẽ áp dụng một biến thể của Clean Architecture, với tư tưởng "feature-first" (ưu tiên tổ chức theo tính năng).

### a. Nguyên tắc cốt lõi

1.  **Tổ chức theo Tính năng, không theo Layer:** Thay vì có các thư mục `controllers`, `services` ở cấp cao nhất, chúng ta sẽ nhóm code theo từng tính năng nghiệp vụ (e.g., `tasks`, `workspaces`, `users`).
2.  **Quy tắc Phụ thuộc (Dependency Rule):** Các layer bên trong (logic nghiệp vụ) không được biết gì về các layer bên ngoài (framework, database, UI). Ví dụ: Service layer không được `import FastAPI` hay `import Express`.
3.  **Phân tách Trách nhiệm (Separation of Concerns):** Mỗi module chỉ làm một việc duy nhất.
4.  **Vertical Slicing:** Mỗi feature được implement từ đầu đến cuối (database → service → API → tests) trước khi chuyển sang feature tiếp theo.

### b. Cấu trúc thư mục chi tiết

```
src/
├── core/                           # Shared infrastructure và utilities
│   ├── __init__.py
│   ├── database/                   # Database connection và utilities
│   │   ├── __init__.py
│   │   └── connection.py           # MongoDB connection pooling
│   ├── notion/                     # Notion SDK wrapper
│   │   ├── __init__.py
│   │   ├── client.py               # Notion client initialization
│   │   └── rate_limiter.py         # Rate limit handling với exponential backoff
│   └── errors/                     # Error handling
│       ├── __init__.py
│       ├── error_handler.py        # Global error handler middleware
│       └── exceptions.py           # Custom exception classes
│
├── config/                         # Configuration management
│   ├── __init__.py
│   └── settings.py                 # Environment variables và settings (Pydantic Settings)
│
├── features/                       # Feature modules (vertical slices)
│   │
│   ├── tasks/                      # Task management feature
│   │   ├── __init__.py
│   │   ├── routes.py               # API endpoints (FastAPI router hoặc Express router)
│   │   ├── services/               # Business logic layer
│   │   │   ├── __init__.py
│   │   │   └── notion_task_service.py
│   │   ├── dto/                    # Data Transfer Objects (Request/Response models)
│   │   │   ├── __init__.py
│   │   │   ├── create_task_request.py
│   │   │   ├── create_task_response.py
│   │   │   ├── list_tasks_request.py
│   │   │   ├── list_tasks_response.py
│   │   │   ├── update_task_request.py
│   │   │   └── update_task_response.py
│   │   └── repository.py           # Data access layer (nếu cần cache hoặc DB local)
│   │
│   ├── workspaces/                 # Workspace mapping feature
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── workspace_service.py
│   │   ├── dto/
│   │   │   ├── __init__.py
│   │   │   ├── create_workspace_request.py
│   │   │   └── workspace_response.py
│   │   ├── models.py               # MongoDB schema (Workspace document)
│   │   └── repository.py           # Database operations
│   │
│   └── users/                      # User mapping feature
│       ├── __init__.py
│       ├── routes.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── user_mapping_service.py
│       ├── dto/
│       │   ├── __init__.py
│       │   ├── create_user_mapping_request.py
│       │   └── user_mapping_response.py
│       ├── models.py               # MongoDB schema (User mapping document)
│       └── repository.py
│
├── adapters/                       # Platform-specific adapters (Teams, Slack, etc.)
│   ├── __init__.py
│   ├── base_adapter.py             # Abstract base class
│   ├── teams/
│   │   ├── __init__.py
│   │   ├── teams_adapter.py        # Teams-specific logic
│   │   └── adaptive_cards.py       # Adaptive Cards formatting
│   └── slack/
│       ├── __init__.py
│       ├── slack_adapter.py        # Slack-specific logic
│       └── block_kit.py            # Block Kit formatting
│
├── tests/                          # Test files mirroring src structure
│   ├── unit/
│   │   ├── test_tasks_service.py
│   │   └── test_workspaces_service.py
│   └── integration/
│       ├── test_tasks_api.py
│       └── test_notion_integration.py
│
└── main.py                         # Application entrypoint
```

### c. File Naming Patterns

| Mục đích | Python | TypeScript/JavaScript |
|----------|--------|----------------------|
| API Routes | `routes.py` | `routes.ts` hoặc `controller.ts` |
| Business Logic | `services/notion_task_service.py` | `services/notionTaskService.ts` |
| Request DTOs | `dto/create_task_request.py` | `dto/createTaskRequest.ts` |
| Response DTOs | `dto/create_task_response.py` | `dto/createTaskResponse.ts` |
| Database Models | `models.py` | `models.ts` |
| Repository | `repository.py` | `repository.ts` |
| Adapters | `teams_adapter.py` | `teamsAdapter.ts` |

---

## 4. Ví dụ Luồng hoạt động: Tạo Task mới

Để làm rõ kiến trúc, đây là luồng xử lý chi tiết của một request `POST /tasks`:

### Request Flow Diagram

```
Client
  ↓
POST /tasks {"title": "Fix bug", "notion_database_id": "abc123"}
  ↓
main.py (Application entrypoint)
  ↓
features/tasks/routes.py (API Layer)
  ↓
features/tasks/dto/create_task_request.py (Validation)
  ↓
features/tasks/services/notion_task_service.py (Business Logic)
  ↓
core/notion/client.py (Notion SDK với rate limiting)
  ↓
Notion API
```

### Chi tiết từng bước:

#### 1. Request từ Client
Client gửi HTTP POST request:
```json
POST /tasks
{
  "title": "Fix login bug",
  "notion_database_id": "abc-123-def-456",
  "assignee_id": "user_001",
  "priority": "High"
}
```

#### 2. Application Entrypoint (`main.py`)
```python
# main.py
from fastapi import FastAPI
from features.tasks.routes import router as tasks_router

app = FastAPI()
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
```

`main.py` đã đăng ký router từ feature `tasks`, request được chuyển đến `features/tasks/routes.py`.

#### 3. API Layer (`features/tasks/routes.py`)

**Nhiệm vụ:** Xử lý HTTP request/response, validation, dependency injection

```python
# features/tasks/routes.py
from fastapi import APIRouter, Depends, status
from .dto.create_task_request import CreateTaskRequest
from .dto.create_task_response import CreateTaskResponse
from .services.notion_task_service import NotionTaskService

router = APIRouter()

@router.post("/", response_model=CreateTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: CreateTaskRequest,
    task_service: NotionTaskService = Depends()
):
    """Create a new task in Notion database."""
    # Request body đã được validate tự động bởi Pydantic
    # Gọi service layer
    response = await task_service.create_task(request)
    return response
```

**Lưu ý:**
- Không chứa business logic
- Chỉ lo validation, HTTP status codes, response formatting
- Inject dependencies (service) qua Depends()

#### 4. DTO Layer - Request Validation (`features/tasks/dto/create_task_request.py`)

**Nhiệm vụ:** Định nghĩa cấu trúc dữ liệu và validation rules

```python
# features/tasks/dto/create_task_request.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class CreateTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    notion_database_id: str = Field(..., description="Target Notion database ID")
    assignee_id: Optional[str] = Field(None, description="Platform user ID to assign")
    due_date: Optional[datetime] = None
    priority: Optional[str] = Field(None, description="Priority: Low, Medium, High")
    properties: Optional[dict] = Field(default_factory=dict)

    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in ['Low', 'Medium', 'High']:
            raise ValueError('Priority must be Low, Medium, or High')
        return v
```

#### 5. Service Layer (`features/tasks/services/notion_task_service.py`)

**Nhiệm vụ:** Business logic, orchestration, không biết gì về HTTP

```python
# features/tasks/services/notion_task_service.py
from ..dto.create_task_request import CreateTaskRequest
from ..dto.create_task_response import CreateTaskResponse
from core.notion.client import get_notion_client
from core.errors.exceptions import NotFoundError, NotionAPIError
from features.users.services.user_mapping_service import UserMappingService

class NotionTaskService:
    def __init__(self):
        self.notion_client = get_notion_client()
        self.user_mapping_service = UserMappingService()

    async def create_task(self, request: CreateTaskRequest) -> CreateTaskResponse:
        # Business Logic 1: Resolve assignee nếu có
        notion_assignee_id = None
        if request.assignee_id:
            notion_assignee_id = await self.user_mapping_service.resolve_notion_user_id(
                platform="web",  # Hoặc lấy từ context
                platform_user_id=request.assignee_id
            )

        # Business Logic 2: Build Notion properties
        properties = {
            "Name": {"title": [{"text": {"content": request.title}}]},
        }

        if notion_assignee_id:
            properties["Assignee"] = {"people": [{"id": notion_assignee_id}]}

        if request.due_date:
            properties["Due Date"] = {"date": {"start": request.due_date.isoformat()}}

        if request.priority:
            properties["Priority"] = {"select": {"name": request.priority}}

        # Merge custom properties
        properties.update(request.properties)

        # Call Notion API (với rate limiting được handle trong client)
        try:
            notion_page = await self.notion_client.pages.create(
                parent={"database_id": request.notion_database_id},
                properties=properties
            )
        except Exception as e:
            # Map Notion errors to domain errors
            raise NotionAPIError(f"Failed to create task: {str(e)}")

        # Return response
        return CreateTaskResponse(
            notion_task_id=notion_page["id"],
            notion_task_url=notion_page["url"],
            created_at=notion_page["created_time"]
        )
```

**Lưu ý:**
- Không import FastAPI, HTTP concepts
- Nhận và trả về domain objects (DTOs)
- Chứa toàn bộ business logic
- Orchestrate calls đến các services khác (UserMappingService)

#### 6. Notion Client Layer (`core/notion/client.py`)

**Nhiệm vụ:** Wrap Notion SDK, xử lý rate limiting, timeout

```python
# core/notion/client.py
from notion_client import AsyncClient
from config.settings import get_settings
from .rate_limiter import with_retry

settings = get_settings()
_notion_client = None

def get_notion_client() -> AsyncClient:
    global _notion_client
    if _notion_client is None:
        _notion_client = AsyncClient(auth=settings.NOTION_API_KEY)
    return _notion_client
```

#### 7. Response DTO (`features/tasks/dto/create_task_response.py`)

```python
# features/tasks/dto/create_task_response.py
from pydantic import BaseModel
from datetime import datetime

class CreateTaskResponse(BaseModel):
    notion_task_id: str
    notion_task_url: str
    created_at: datetime
```

### Tóm tắt Trách nhiệm từng Layer

| Layer | File | Trách nhiệm | Không được làm |
|-------|------|-------------|----------------|
| **API** | `routes.py` | HTTP handling, validation, DI | Business logic, DB access |
| **DTO** | `dto/*.py` | Data structure, validation rules | Logic, side effects |
| **Service** | `services/*.py` | Business logic, orchestration | HTTP concepts, DB details |
| **Infrastructure** | `core/notion/client.py` | External API communication | Business logic |

---

## 5. Best Practices cụ thể

### a. Dependency Injection
- Sử dụng FastAPI Depends() hoặc NestJS dependency injection
- Services không được khởi tạo dependencies trong constructor một cách hard-coded
- Dễ dàng mock dependencies trong tests

### b. Error Handling
- Service layer throw domain exceptions (`NotFoundError`, `ValidationError`, `NotionAPIError`)
- Global error handler middleware map exceptions → HTTP status codes
- Client nhận standardized error response format

```python
# core/errors/exceptions.py
class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class NotFoundError(DomainException):
    """Entity not found"""
    pass

class NotionAPIError(DomainException):
    """Notion API failed"""
    pass
```

### c. Testing Strategy

**Unit Tests** (Service layer):
```python
# tests/unit/test_notion_task_service.py
def test_create_task_with_assignee():
    # Mock dependencies
    mock_notion_client = Mock()
    mock_user_mapping_service = Mock()
    mock_user_mapping_service.resolve_notion_user_id.return_value = "notion_user_123"

    # Test service logic in isolation
    service = NotionTaskService()
    service.notion_client = mock_notion_client
    service.user_mapping_service = mock_user_mapping_service

    # Execute
    request = CreateTaskRequest(title="Test", notion_database_id="db_123", assignee_id="user_001")
    response = service.create_task(request)

    # Assert
    assert mock_user_mapping_service.resolve_notion_user_id.called
    assert mock_notion_client.pages.create.called
```

**Integration Tests** (API layer):
```python
# tests/integration/test_tasks_api.py
def test_create_task_endpoint(test_client):
    # Test end-to-end flow
    response = test_client.post("/tasks", json={
        "title": "Integration test task",
        "notion_database_id": "real_test_db_id"
    })

    assert response.status_code == 201
    assert "notion_task_id" in response.json()
```

### d. Khi nào tạo Repository Layer?

Không phải lúc nào cũng cần `repository.py`. Chỉ tạo khi:
- Cần cache dữ liệu từ Notion trong MongoDB
- Cần aggregate data từ nhiều nguồn
- Logic query phức tạp cần tái sử dụng

Nếu chỉ gọi Notion SDK trực tiếp, Service có thể gọi `core/notion/client.py` luôn.

---

## 6. Kết luận

Việc tuân thủ kiến trúc và các quy tắc trên sẽ giúp dự án:

- **Dễ bảo trì:** Khi cần sửa lỗi của tính năng "tasks", chúng ta biết chính xác cần tìm ở đâu (`features/tasks/`).
- **Dễ kiểm thử (Testable):** Có thể test riêng service layer mà không cần khởi động web server.
- **Dễ mở rộng:** Thêm một tính năng mới chỉ đơn giản là tạo một thư mục mới trong `features/` mà không ảnh hưởng đến các tính năng cũ.
- **Vertical Slicing:** Có thể ship từng feature độc lập, nhận feedback sớm.
- **Testable:** Mỗi layer có thể test độc lập với mocks.
- **Framework-agnostic Business Logic:** Có thể chuyển từ FastAPI sang Flask/Django mà không cần sửa service layer.
