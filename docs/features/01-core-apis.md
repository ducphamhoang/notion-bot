# Feature Spec: Core Task APIs & Database

**Status:** Not Started
**Owner:** TBD
**Related PRD:** ../../prd.md

---

### 1. Problem
Để quản lý task trong Notion, người dùng hoặc các hệ thống khác cần một phương thức truy cập có lập trình (programmatic access) thay vì phải thao tác thủ công trên giao diện Notion. Hệ thống cần một bộ API ổn định để thực hiện các thao tác CRUD (Create, Read, Update, Delete) trên các task.

### 2. User Stories / Scenarios
- **As a developer (backend),** I want to implement API endpoints so that other services can manage Notion tasks.
- **As a developer (frontend),** I want to call these APIs from a client application to create and view tasks.
- **As an external system (e.g., CI/CD pipeline),** I want to call an API to automatically create a task when a build fails.

### 3. Technical Design

#### 3.1. Database & Models (MongoDB)
- **Công nghệ:** Sử dụng MongoDB chạy trên Docker cho môi trường local.
- **Collections:**
    - `workspaces`: Lưu trữ thông tin cấu hình, mapping giữa kênh chat (e.g., Teams channel) và Notion database ID.
        ```json
        {
          "_id": "ObjectId",
          "platform": "teams",
          "platform_id": "teams_channel_id_abc",
          "notion_database_id": "notion_db_id_xyz",
          "name": "Project X Channel"
        }
        ```
    - `users`: Lưu trữ mapping giữa user trên nền tảng chat và user Notion.
        ```json
        {
          "_id": "ObjectId",
          "platform_user_id": "teams_user_id_123",
          "notion_user_id": "notion_user_id_456",
          "display_name": "User A"
        }
        ```
- **Data Models (Code):** Sử dụng Pydantic để định nghĩa và validate các model này trong code FastAPI.

#### 3.2. API Endpoints
Dựa trên `prd.md`, các endpoint cần được implement:
- `POST /tasks`: Tạo task mới.
- `GET /tasks`: Lấy danh sách task, hỗ trợ filter, sort, và pagination.
- `PATCH /tasks/{id}`: Cập nhật task.
- `DELETE /tasks/{id}`: Xóa task.

Logic của các endpoint này sẽ sử dụng `notion-sdk-py` để tương tác với Notion API.

### 4. UI/UX
- Không áp dụng cho phần này. Đây là backend feature.

### 5. Edge Cases & Considerations
- Notion API rate limit: Cần xử lý trường hợp gọi API Notion quá giới hạn.
- Lỗi từ Notion API: Xử lý các mã lỗi (4xx, 5xx) mà Notion API trả về.
- Dữ liệu không hợp lệ: API cần trả về lỗi 400 Bad Request nếu payload từ client không đúng.

### 6. Acceptance Criteria
- [ ] Các API endpoint (CRUD) hoạt động đúng như đặc tả trong OpenAPI/Swagger.
- [ ] Khi gọi API `POST /tasks`, một task mới được tạo thành công trong Notion database tương ứng.
- [ ] Khi gọi `GET /tasks`, dữ liệu trả về khớp với dữ liệu trên Notion.
- [ ] Dữ liệu cấu hình (workspaces, users) được lưu và truy xuất thành công từ MongoDB.
- [ ] Có unit test cho các API endpoint.
