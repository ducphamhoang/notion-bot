# Feature Spec: Microsoft Teams Integration

**Status:** Not Started
**Owner:** TBD
**Related PRD:** ../../prd.md

---

### 1. Problem
Người dùng muốn quản lý công việc trên Notion mà không cần phải rời khỏi môi trường làm việc hàng ngày của họ là Microsoft Teams. Họ cần một con bot có thể được gọi bằng các lệnh đơn giản để tương tác với Notion.

### 2. User Stories / Scenarios
- **As a Teams user,** I want to type a slash command like `/task create title:"New feature"` in a channel to quickly create a task in the Notion database linked to that channel.
- **As a Teams user,** I want to receive notifications (e.g., task assigned to me, task overdue) directly in Teams as messages from the bot. (Lưu ý: phần notification thuộc Rule Engine, sẽ làm ở phase sau, nhưng thiết kế cần hướng tới việc này).

### 3. Technical Design

#### 3.1. Webhook Endpoint
- **Endpoint:** `POST /webhooks/teams`
- **Xác thực:** Request từ Teams phải được xác thực bằng cơ chế HMAC signature. Backend sẽ lưu một secret key và dùng nó để kiểm tra hash của payload, đảm bảo request thực sự đến từ Teams.

#### 3.2. Teams Adapter
- **Vai trò:** Là một module/class chịu trách nhiệm xử lý các logic riêng cho Teams.
- **Nhiệm vụ:**
    1.  **Parsing:** Nhận payload từ webhook, phân tích và trích xuất các thông tin quan trọng: người gửi, nội dung lệnh, channel...
    2.  **Command Handling:** Chuyển đổi lệnh từ Teams (e.g., `/task list`) thành một lời gọi đến service/API nội bộ của Core Bot Engine.
    3.  **Formatting:** Nhận kết quả từ Core Bot Engine và định dạng nó thành một cấu trúc mà Teams hiểu được, cụ thể là **Adaptive Cards**. Việc này giúp hiển thị thông tin một cách phong phú và có tương tác (buttons, etc.).

#### 3.3. Luồng hoạt động (Slash Command)
1. Người dùng gõ `/task ...` trong Teams.
2. Teams gửi một HTTP POST request đến `https://your-bot-url/webhooks/teams`.
3. Webhook endpoint xác thực HMAC signature.
4. Payload được chuyển đến `TeamsAdapter`.
5. `TeamsAdapter` phân tích lệnh và gọi đến service tương ứng (e.g., `TaskService.create_task(...)`).
6. `TaskService` xử lý logic, gọi Notion API và trả kết quả về cho `TeamsAdapter`.
7. `TeamsAdapter` tạo một Adaptive Card để hiển thị kết quả (e.g., "✅ Task '...' đã được tạo thành công.") và gửi lại cho Teams.
8. Người dùng thấy phản hồi của bot trong channel.

### 4. UI/UX
- Phản hồi của bot trong Teams sẽ sử dụng Adaptive Cards để hiển thị thông tin một cách trực quan.
- Cần thiết kế một vài mẫu Adaptive Card cơ bản cho các phản hồi:
    - Tin nhắn thành công.
    - Tin nhắn báo lỗi.
    - Hiển thị danh sách task.

### 5. Edge Cases & Considerations
- **Timeout:** Teams yêu cầu phản hồi gần như tức thì cho một slash command. Nếu logic xử lý mất nhiều thời gian, bot cần gửi một phản hồi "ack" ngay lập tức, sau đó gửi một tin nhắn tiếp theo (proactive message) với kết quả thực sự.
- **Cấu hình kênh:** Cần có cơ chế để map một channel trong Teams với một Notion Database ID. Thông tin này sẽ được lưu trong collection `workspaces` ở MongoDB.

### 6. Acceptance Criteria
- [ ] Bot được cài đặt thành công vào một team trong MS Teams.
- [ ] Endpoint `/webhooks/teams` xác thực thành công request từ Teams.
- [ ] Khi người dùng gõ một slash command hợp lệ, bot phản hồi lại trong channel.
- [ ] Lệnh `/task create` tạo ra một task mới trong Notion database đã được cấu hình cho channel đó.
- [ ] Phản hồi của bot được hiển thị dưới dạng Adaptive Card.
