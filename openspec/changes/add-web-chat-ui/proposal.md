# Change: Add Simple Web Chat UI for Bot Testing

## Why
During MVP development, testing bot commands through integrated platforms (Teams, Slack) is slow and requires full environment setup. Developers and testers need a simple, fast web interface to interact with the Core Bot Engine APIs directly for rapid testing and validation of task management commands (`/task create`, `/task list`, etc.) before deploying to production chat platforms.

## What Changes
- Add a minimal single-page web application (SPA) for chat-based bot interaction
- Implement command parser to convert user input (e.g., `/task list status:open`) into API calls
- Create UI components for message display, input field, and loading states
- Add error handling and user-friendly error display for API failures
- Support basic task commands through direct RESTful API integration
- Use simple authentication (API key for MVP) to access backend APIs

## Impact
- Affected specs: `web-chat-ui` (new capability)
- Affected code:
  - New frontend application directory (e.g., `frontend/` or `web-chat/`)
  - Static file serving configuration in main API server
  - Optional CORS configuration for development environment
  - New npm/yarn dependencies for React/Vite or vanilla JavaScript
- Dependencies:
  - React + Vite (or vanilla HTML/CSS/JS)
  - Optional UI library: Pico.css or Chakra UI
  - Existing Core Task APIs (dependency on `task-api` capability)
