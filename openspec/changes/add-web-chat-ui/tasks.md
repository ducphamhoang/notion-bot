# Implementation Tasks - Web Chat UI

**Tech Stack Decision:** React 18 + Vite + TypeScript + Tailwind CSS + shadcn/ui

**Architecture Alignment:** Frontend served via FastAPI StaticFiles, follows existing backend structure in `src/features/`

## 0. Architecture Decisions & Planning
- [x] 0.1 Tech stack: React + Vite + TypeScript + Tailwind + shadcn/ui Command component for slash autocomplete
- [ ] 0.2 Directory structure: `frontend/` at project root (separate from backend `src/`)
- [ ] 0.3 Static file serving: FastAPI StaticFiles middleware for production build (`frontend/dist`)
- [ ] 0.4 API integration: Use existing endpoints from `src/features/tasks/routes.py`
- [ ] 0.5 Type safety: Generate TypeScript types matching Python Pydantic DTOs

## 1. Project Setup
- [ ] 1.1 Initialize Vite + React + TypeScript project: `npm create vite@latest frontend -- --template react-ts`
- [ ] 1.2 Install core dependencies: `cd frontend && npm install`
- [ ] 1.3 Setup Tailwind CSS: `npm install -D tailwindcss postcss autoprefixer && npx tailwindcss init -p`
- [ ] 1.4 Configure Tailwind in `tailwind.config.js` with content paths
- [ ] 1.5 Install shadcn/ui CLI and initialize: `npx shadcn-ui@latest init`
- [ ] 1.6 Add shadcn Command component: `npx shadcn-ui@latest add command`
- [ ] 1.7 Add additional shadcn components: `npx shadcn-ui@latest add button card input scroll-area`
- [ ] 1.8 Update backend `.env`: Add `http://localhost:5173` to `CORS_ORIGINS` for dev mode
- [ ] 1.9 Create `frontend/.env` with `VITE_API_BASE_URL=http://localhost:8000`

## 2. Core UI Components
- [ ] 2.1 Create `frontend/src/components/ChatContainer.tsx` - Main layout with header and message area
- [ ] 2.2 Create `frontend/src/components/MessageList.tsx` - Scrollable message history with auto-scroll to bottom
- [ ] 2.3 Create `frontend/src/components/Message.tsx` - Individual message bubble (user vs bot styling, timestamp)
- [ ] 2.4 Create `frontend/src/components/CommandInput.tsx` - Input field with slash command trigger
- [ ] 2.5 Create `frontend/src/components/LoadingIndicator.tsx` - Spinner for API call states
- [ ] 2.6 Create `frontend/src/components/TaskCard.tsx` - Formatted display for task data responses
- [ ] 2.7 Style all components with Tailwind for minimal, clean appearance

## 3. Slash Command Autocomplete ⭐
- [ ] 3.1 Create `frontend/src/lib/commands.ts` with command registry:
  ```ts
  export const COMMANDS = [
    {
      value: 'create',
      label: '/task create',
      description: 'Create a new task in Notion',
      params: ['title', 'priority?', 'assignee_id?', 'due_date?']
    },
    {
      value: 'list',
      label: '/task list',
      description: 'List tasks with optional filters',
      params: ['status?', 'assignee_id?', 'priority?']
    },
    {
      value: 'update',
      label: '/task update',
      description: 'Update task properties',
      params: ['task_id', 'title?', 'status?', 'priority?']
    },
    {
      value: 'delete',
      label: '/task delete',
      description: 'Archive a task in Notion',
      params: ['task_id']
    }
  ]
  ```
- [ ] 3.2 Create `frontend/src/components/CommandPalette.tsx` using shadcn Command component
- [ ] 3.3 Implement trigger: Show dropdown when user types "/" at start of input
- [ ] 3.4 Filter commands as user types (e.g., "/task c" shows only "create")
- [ ] 3.5 Keyboard navigation: Arrow keys (↑↓) + Enter to select, Escape to close
- [ ] 3.6 Auto-insert selected command into input field with cursor after command
- [ ] 3.7 Show parameter hints after command selection (e.g., "title:... priority:...")

## 4. Command Parser Implementation
- [ ] 4.1 Create `frontend/src/lib/commandParser.ts` - Parse text like `/task create title:"Fix bug" priority:High`
- [ ] 4.2 Implement key-value parser handling quoted strings: `parseParams(text: string): Record<string, string>`
- [ ] 4.3 Handle edge cases: escaped quotes, special characters, spaces in values
- [ ] 4.4 Create command-to-endpoint mapper:
  - `/task create` → `POST /tasks` with CreateTaskRequest body
  - `/task list` → `GET /tasks?status=...&assignee_id=...` with query params
  - `/task update {id}` → `PATCH /tasks/{id}` with UpdateTaskRequest body
  - `/task delete {id}` → `DELETE /tasks/{id}`
- [ ] 4.5 Validate required parameters per command (show inline errors)
- [ ] 4.6 Create `frontend/src/lib/apiMapper.ts` to convert parsed params to API request format

## 5. TypeScript Types (Matching Backend DTOs)
- [ ] 5.1 Create `frontend/src/types/task.ts` with interfaces matching backend `src/features/tasks/dto/`:
  ```ts
  // Matches CreateTaskRequest from src/features/tasks/dto/create_task_request.py
  export interface CreateTaskRequest {
    title: string;
    notion_database_id: string;
    assignee_id?: string;
    due_date?: string; // ISO 8601 datetime
    priority?: 'Low' | 'Medium' | 'High';
    properties?: Record<string, any>;
  }

  // Matches CreateTaskResponse
  export interface CreateTaskResponse {
    notion_task_id: string;
    notion_task_url: string;
    created_at: string;
  }

  // Matches ListTasksRequest (query params)
  export interface ListTasksRequest {
    notion_database_id: string;
    status?: string;
    assignee_id?: string;
    priority?: string;
    page_size?: number;
    start_cursor?: string;
  }

  // Matches ListTasksResponse
  export interface ListTasksResponse {
    tasks: Task[];
    has_more: boolean;
    next_cursor?: string;
  }

  // Matches UpdateTaskRequest
  export interface UpdateTaskRequest {
    title?: string;
    status?: string;
    assignee_id?: string;
    due_date?: string;
    priority?: 'Low' | 'Medium' | 'High';
    properties?: Record<string, any>;
  }

  // Matches UpdateTaskResponse
  export interface UpdateTaskResponse {
    notion_task_id: string;
    notion_task_url: string;
    updated_at: string;
  }
  ```
- [ ] 5.2 Create `frontend/src/types/api.ts` for common API types (error responses, pagination)
- [ ] 5.3 Create `frontend/src/types/message.ts` for chat message types

## 6. API Integration (Aligned with Existing Backend)
- [ ] 6.1 Create `frontend/src/api/client.ts` - Axios/fetch wrapper with base URL and auth headers
- [ ] 6.2 Create `frontend/src/api/taskApi.ts` with functions calling existing backend endpoints:
  - `createTask(data: CreateTaskRequest): Promise<CreateTaskResponse>`
  - `listTasks(params: ListTasksRequest): Promise<ListTasksResponse>`
  - `updateTask(taskId: string, data: UpdateTaskRequest): Promise<UpdateTaskResponse>`
  - `deleteTask(taskId: string): Promise<void>`
- [ ] 6.3 Implement authentication: Add `X-API-Key` or `Authorization: Bearer <token>` header
- [ ] 6.4 Handle domain exceptions from backend global handler:
  - 404 NotFoundError → "Task not found"
  - 400 ValidationError → Show validation details
  - 502/503 NotionAPIError → "Notion API error, please try again"
- [ ] 6.5 Add request timeout (30s) with `AbortController`
- [ ] 6.6 Add retry logic for network errors (exponential backoff, max 3 retries)
- [ ] 6.7 Create error response parser to extract user-friendly messages

## 7. State Management
- [ ] 7.1 Create `frontend/src/store/chatStore.ts` using Zustand or React Context:
  - Message history: `messages: Array<{id, role, content, timestamp, error?}>`
  - Loading state: `isLoading: boolean`
  - Auth state: `apiKey: string | null`
- [ ] 7.2 Implement `addMessage(message)` action with optimistic updates
- [ ] 7.3 Implement `sendCommand(text)` action orchestrating parser → API call → response
- [ ] 7.4 Store API key in `sessionStorage` (not localStorage for security)
- [ ] 7.5 Handle input field state: current value, autocomplete visibility

## 8. User Experience Enhancements
- [ ] 8.1 Auto-focus input field on page load and after sending message
- [ ] 8.2 Enter to submit command, Shift+Enter for newline (if multi-line supported later)
- [ ] 8.3 Add relative timestamps: "just now", "2m ago", "1h ago" using `date-fns`
- [ ] 8.4 Format task list responses as cards with:
  - Task title (bold)
  - Status badge (color-coded)
  - Priority indicator
  - Assignee name
  - Due date (if set)
  - Link to Notion page
- [ ] 8.5 Message type indicators:
  - User message: Right-aligned blue bubble
  - Bot response: Left-aligned gray bubble
  - Error message: Left-aligned red bubble with icon
- [ ] 8.6 Show typing indicator ("Bot is thinking...") during API calls
- [ ] 8.7 Add success animations (checkmark) for successful commands
- [ ] 8.8 Command history: Press ↑ arrow to recall previous command

## 9. Responsive Design
- [ ] 9.1 Mobile-first approach with Tailwind breakpoints:
  - Base: 320px (mobile)
  - `sm:` 640px
  - `md:` 768px (tablet)
  - `lg:` 1024px+ (desktop)
- [ ] 9.2 Test layout on iPhone SE (320px), iPad (768px), desktop (1920px)
- [ ] 9.3 Ensure touch targets are minimum 44x44px (buttons, command items)
- [ ] 9.4 Use `ScrollArea` from shadcn for message list on mobile
- [ ] 9.5 Test on actual devices: Chrome DevTools mobile emulator + real phone
- [ ] 9.6 Add PWA meta tags for "Add to Home Screen" functionality (optional)

## 10. Authentication Setup
- [ ] 10.1 Create `frontend/src/components/AuthModal.tsx` - Prompt for API key on first load
- [ ] 10.2 Validate API key format (non-empty string, starts with "secret_" for Notion)
- [ ] 10.3 Store API key in sessionStorage: `sessionStorage.setItem('apiKey', key)`
- [ ] 10.4 Add "Logout" button to clear API key and reset chat
- [ ] 10.5 Handle 401/403 responses: Show "Invalid API key" error and prompt re-authentication
- [ ] 10.6 Create `.env.example` in frontend/ with:
  ```
  VITE_API_BASE_URL=http://localhost:8000
  VITE_DEFAULT_DATABASE_ID=your-notion-database-id-here
  ```
- [ ] 10.7 Document in README: "Get NOTION_API_KEY from backend .env file for testing"

## 11. Backend Integration (FastAPI Static Files)
- [ ] 11.1 Add StaticFiles middleware to `src/main.py`:
  ```python
  from fastapi.staticfiles import StaticFiles
  import os

  # Serve frontend build (only if dist/ exists)
  frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
  if os.path.exists(frontend_dist):
      app.mount("/chat", StaticFiles(directory=frontend_dist, html=True), name="chat")
  ```
- [ ] 11.2 Update `Dockerfile` to install Node.js and build frontend:
  ```dockerfile
  # Multi-stage build
  FROM node:18-alpine AS frontend-builder
  WORKDIR /app/frontend
  COPY frontend/package*.json ./
  RUN npm ci
  COPY frontend/ ./
  RUN npm run build

  FROM python:3.11-slim
  # ... existing Python setup ...
  COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
  ```
- [ ] 11.3 Update `docker-compose.yml` to mount frontend/ for development:
  ```yaml
  volumes:
    - ./src:/app/src:ro
    - ./frontend:/app/frontend  # Enable hot-reload for dev
  ```
- [ ] 11.4 Update `src/config/settings.py` to add `FRONTEND_ENABLED: bool = True`
- [ ] 11.5 Verify CORS_ORIGINS in `.env` includes both dev (`http://localhost:5173`) and prod URLs
- [ ] 11.6 Test production build: `cd frontend && npm run build`, then access `http://localhost:8000/chat`

## 12. Testing and Validation
- [ ] 12.1 Manual test all commands with real Notion database:
  - `/task create title:"Test task" priority:High`
  - `/task list status:open`
  - `/task update {id} status:completed`
  - `/task delete {id}`
- [ ] 12.2 Test slash command autocomplete:
  - Type "/" → See all commands
  - Type "/task c" → Filter to "create"
  - Arrow keys navigation + Enter selection
  - Escape to close palette
- [ ] 12.3 Test parameter parsing edge cases:
  - Quoted strings with spaces: `title:"My task"`
  - Special characters: `title:"Task #1"`
  - Missing required params: Show validation error
  - Invalid param values: Show specific error
- [ ] 12.4 Test error handling:
  - Network failure (disconnect internet)
  - Invalid API key (401 response)
  - Notion API error (503 response)
  - Invalid task ID (404 response)
- [ ] 12.5 Test authentication flow:
  - First load → Prompt for API key
  - Invalid key → Show error, re-prompt
  - Logout → Clear chat and key
- [ ] 12.6 Test loading states:
  - Spinner appears during API call
  - Input disabled while loading
  - Typing indicator visible
- [ ] 12.7 Browser compatibility:
  - Chrome (latest)
  - Firefox (latest)
  - Safari (latest)
  - Edge (latest)
- [ ] 12.8 Responsive design validation:
  - iPhone SE (320px width)
  - iPad (768px width)
  - Desktop (1920px width)
  - Landscape orientation on mobile

## 13. Build & Deployment
- [ ] 13.1 Create `frontend/vite.config.ts` with production optimizations:
  ```ts
  export default defineConfig({
    build: {
      outDir: 'dist',
      sourcemap: false,
      minify: 'terser',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            ui: ['@radix-ui/react-command', '@radix-ui/react-dialog']
          }
        }
      }
    }
  })
  ```
- [ ] 13.2 Add build script to `package.json`: `"build": "tsc && vite build"`
- [ ] 13.3 Add deployment script to root `deploy.sh`:
  ```bash
  cd frontend
  npm install
  npm run build
  cd ..
  docker-compose down
  docker-compose build
  docker-compose up -d
  ```
- [ ] 13.4 Test production build locally: `npm run build && npm run preview`
- [ ] 13.5 Verify bundle size: Target < 200KB gzipped

## 14. Documentation
- [ ] 14.1 Create `frontend/README.md` with:
  - Development setup: `npm install && npm run dev`
  - Build command: `npm run build`
  - Environment variables: Copy `.env.example` to `.env`
  - Tech stack overview
- [ ] 14.2 Document supported commands in `frontend/COMMANDS.md`:
  - Command syntax
  - Parameter descriptions
  - Example usage
  - Expected responses
- [ ] 14.3 Add screenshots to `openspec/changes/add-web-chat-ui/`:
  - Slash command autocomplete in action
  - Task creation flow
  - Task list display
  - Error handling examples
- [ ] 14.4 Update main `README.md` with Web Chat UI section:
  - Access URL: `http://localhost:8000/chat`
  - Authentication instructions
  - Link to frontend/README.md
- [ ] 14.5 Create troubleshooting guide in `docs/WEBCHAT_TROUBLESHOOTING.md`:
  - CORS errors → Check .env CORS_ORIGINS
  - Authentication issues → Verify API key format
  - Build failures → Node version mismatch
  - Notion API errors → Check database permissions
