# Feature Spec: Simple Web Chat UI

**Status:** Not Started
**Owner:** TBD
**Related PRD:** ../../prd.md

---

### 1. Problem
Trong giai đoạn đầu, việc tích hợp và kiểm thử bot trên các nền tảng như Teams/Slack có thể chậm và phức tạp. Lập trình viên cần một giao diện đơn giản, nhanh chóng để có thể tương tác và kiểm thử trực tiếp các API của Core Bot Engine.

### 2. User Stories / Scenarios
- **As a developer,** I want a web-based chat interface so I can quickly test commands (e.g., `/task create`, `/task list`) without needing to set up a full MS Teams environment.
- **As a project manager/tester,** I want to use the web chat to demo and validate the core functionalities of the bot before they are deployed to production chat platforms.

### 3. Technical Design
- **Công nghệ:** React (khởi tạo bằng Vite) hoặc một trang HTML/CSS/JS đơn giản.
- **Kiến trúc:**
    - Đây là một Single Page Application (SPA).
    - Giao diện sẽ gọi trực tiếp đến các RESTful API của Core Bot Engine (e.g., `GET /tasks`, `POST /tasks`).
    - Để đơn giản cho MVP, việc xác thực có thể dùng một API key được hardcode tạm thời.
- **Luồng hoạt động:**
    1. Người dùng truy cập trang web.
    2. Giao diện hiển thị một ô nhập liệu và một khu vực hiển thị tin nhắn.
    3. Người dùng gõ một lệnh (ví dụ: `/task list status:open`).
    4. Khi nhấn Enter, frontend sẽ phân tích sơ bộ lệnh và gọi đến API tương ứng của backend.
    5. Backend xử lý và trả về kết quả (JSON).
    6. Frontend nhận kết quả, định dạng lại cho dễ đọc và hiển thị trong khu vực tin nhắn.

### 4. UI/UX
- Giao diện cực kỳ tối giản:
    - Một panel chính để hiển thị lịch sử chat (câu lệnh và phản hồi).
    - Một ô input ở dưới cùng để người dùng nhập lệnh.
- Không cần thiết kế phức tạp hay màu sắc cầu kỳ ở giai đoạn này. Có thể sử dụng một thư viện component UI đơn giản như `Pico.css` hoặc `Chakra UI` để có giao diện sạch sẽ nhanh chóng.

### 5. Edge Cases & Considerations
- Lỗi API: Giao diện cần hiển thị thông báo lỗi một cách thân thiện khi API backend trả về lỗi.
- Trạng thái loading: Nên có chỉ báo loading trong khi chờ API phản hồi.

### 6. Acceptance Criteria
- [ ] Giao diện web có thể truy cập được trên trình duyệt.
- [ ] Người dùng có thể nhập lệnh vào ô input và gửi đi.
- [ ] Khi gửi lệnh `/task list`, kết quả danh sách task được hiển thị trên giao diện.
- [ ] Khi gửi lệnh `/task create`, thông báo thành công hoặc thất bại được hiển thị.
- [ ] Hiển thị thông báo lỗi nếu API không thể xử lý yêu cầu.
