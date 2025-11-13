# Project Context

## Purpose
Build a centralized backend bot for task management that integrates with Notion API and provides multi-platform chat integration (Teams, Slack, Discord, Telegram) through RESTful APIs and webhooks. The system enables users to create, query, update task status, and receive notifications directly within their chat applications without leaving their workflow.

**Primary Goals:**
- Provide CRUD operations for Notion tasks via RESTful API
- Enable multi-platform chat integrations via webhook endpoints
- Support structured command processing for MVP
- Build scalable architecture ready for future AI agent integration (Google ADK)
- Ensure security, extensibility, and maintainability

## Tech Stack

### Backend (MVP)
- **Language/Framework:** Python (FastAPI) or Node.js (Express/NestJS)
- **Notion Integration:** `notion-sdk-py` (Python) or `@notionhq/client` (Node.js)
- **Validation:** Pydantic (Python) for data models and validation

### Database & Caching
- **Primary Database:** MongoDB
  - Local/MVP: MongoDB in Docker
  - Production: MongoDB Atlas or Google Firestore
- **Caching:** Redis (for caching Notion API responses, reducing API calls)

### Frontend (MVP)
- **Web Chat UI:** React (Vite) or Vue, or simple HTML/CSS/JavaScript
- **UI Library:** Pico.css or Chakra UI (for minimal, clean interface)

### Security & Authentication
- **API Authentication:** JWT tokens
- **User Authentication:** OAuth 2.0 flow for Notion integration
- **Webhook Security:** HMAC signature verification
- **Secrets Management:** Encrypted at-rest and in-transit

### Infrastructure & Deployment
- **Containerization:** Docker
- **Orchestration:** Kubernetes (production) or Docker Compose (development)
- **Deployment Options:** Azure, AWS, Heroku, or other PaaS
- **Message Queue:** RabbitMQ or AWS SQS (for reliable webhook processing)

### Future/Planned
- **AI Agents:** Google ADK (Agent Development Kit)
- **NLP Processing:** Google Cloud AI Platform
- **Agent Tools:** MCP (Model-Centric Platform) with Notion Tool integration

## Project Conventions

### Code Style
- **Python:** Follow PEP 8 conventions, use Black for formatting
- **JavaScript/TypeScript:** Follow ESLint + Prettier configuration
- **Naming Conventions:**
  - Classes: PascalCase (e.g., `TaskService`, `TeamsAdapter`)
  - Functions/Methods: snake_case (Python) or camelCase (JavaScript)
  - Constants: UPPER_SNAKE_CASE
  - API endpoints: kebab-case (e.g., `/api/tasks`, `/webhooks/teams`)

### Architecture Patterns
- **Adapter Pattern:** Core logic remains platform-agnostic. Each chat platform (Teams, Slack, etc.) has its own Adapter class responsible for:
  - Parsing platform-specific payloads
  - Converting to internal command format
  - Formatting responses according to platform requirements (Adaptive Cards for Teams, Block Kit for Slack)

- **Command Dispatcher Pattern:** Routes incoming requests to appropriate handlers based on command type

- **Separation of Concerns:**
  - **API Layer:** Express/FastAPI routes
  - **Service Layer:** Business logic (TaskService, NotionService)
  - **Data Layer:** MongoDB models and queries
  - **Adapter Layer:** Platform-specific integrations

- **Future-Ready for AI:**
  - Core Bot Engine handles structured commands directly
  - Command Dispatcher delegates natural language commands to specialized NLP agents
  - Agents call back to Core APIs with structured data

### Testing Strategy
- **Unit Tests:** Required for all API endpoints and service layer logic
- **Integration Tests:** Test Notion API integration and database operations
- **Load Testing:** System must handle 100+ concurrent requests/second
- **Security Testing:** Validate authentication, authorization, and webhook signature verification
- **Acceptance Criteria:** Each feature must meet defined criteria in feature specs (see `docs/features/`)

### Git Workflow
- **Branch Strategy:** Feature branches from main/master
- **Commit Messages:** Descriptive, imperative mood (e.g., "Add webhook endpoint for Teams")
- **No Force Pushes:** Avoid force pushing to main/master
- **Hooks:** Do not skip pre-commit hooks unless explicitly needed

## Domain Context

### Notion API Integration
- **Rate Limits:** Notion API has rate limits; implement caching and request throttling
- **Database Structure:** Each Notion workspace can have multiple databases; system must support mapping:
  - Chat channel ↔ Notion database ID
  - Chat user ↔ Notion user ID
- **Properties:** Notion tasks have custom properties (status, assignee, due date, priority)

### Command Types (MVP)
In MVP, the bot focuses on **structured commands** rather than natural language processing:
- Slash commands: `/task create title:"Fix bug" assignee:@user due:tomorrow`
- Slash commands: `/task list status:open`
- Future: Natural language commands delegated to AI agents

### Chat Platform Integration
- **Microsoft Teams:**
  - Uses Adaptive Cards for rich message formatting
  - Requires HMAC signature verification for webhooks
  - Slash commands must respond quickly (< 3 seconds) or use proactive messaging

- **Slack:**
  - Uses Block Kit for message formatting
  - Similar webhook security requirements

### User & Workspace Mapping
System maintains mappings between:
- Platform user IDs ↔ Notion user IDs
- Platform channels ↔ Notion database IDs
Stored in MongoDB collections: `users`, `workspaces`

## Important Constraints

### Performance Requirements
- API response time: < 500ms average
- Bot chat response time: < 3 seconds
- System throughput: 100+ requests/second

### Reliability
- Uptime: 99.9%
- Message queue ensures no request loss even during temporary failures
- Graceful degradation when Notion API is unavailable

### Security
- All secrets (tokens, API keys) must be encrypted at rest and in transit
- No sensitive data in logs
- Rate limiting on all API endpoints to prevent abuse
- OAuth 2.0 for user authentication with proper token refresh flow

### Rate Limiting
- Respect Notion API rate limits
- Implement exponential backoff for failed requests
- Cache frequently accessed data in Redis

### Scalability
- Architecture must support horizontal scaling
- Stateless design for easy replication
- Support multiple Notion workspaces/databases per installation

## External Dependencies

### Primary APIs
- **Notion API:** Core dependency for all task operations
  - Official SDK: `notion-sdk-py` or `@notionhq/client`
  - Authentication: Integration tokens or OAuth
  - Rate limits: Must be respected and handled

### Chat Platforms
- **Microsoft Teams:**
  - Bot Framework SDK or direct webhook integration
  - Adaptive Cards for message formatting
  - Webhook signature verification

- **Slack API:**
  - Slack SDK for webhook handling
  - Block Kit for message formatting
  - OAuth for workspace installation

- **Future Platforms:** Discord, Telegram (similar webhook patterns)

### Infrastructure Services
- **MongoDB/MongoDB Atlas:** Primary data store
- **Redis:** Caching layer
- **Message Queue:** RabbitMQ or AWS SQS for async processing

### Future AI Integration
- **Google ADK (Agent Development Kit):** For building NLP agents
- **MCP Notion Tool:** For AI agents to interact with Notion
- **Google Cloud AI Platform:** For advanced language understanding
