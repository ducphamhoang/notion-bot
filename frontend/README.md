# Notion Task Bot - Web Chat UI

React-based web chat interface for interacting with the Notion Task Bot.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS v4** - Styling
- **shadcn/ui** - UI components
- **Zustand** - State management
- **date-fns** - Date formatting

## Development Setup

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The development server will start on `http://localhost:5173`.

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_DEFAULT_DATABASE_ID=your-notion-database-id-here
```

## Building for Production

```bash
# Build the frontend
npm run build

# Preview production build locally
npm run preview
```

The built files will be in the `dist/` directory and will be automatically served by the FastAPI backend at `/chat`.

## Using the Chat Interface

1. **Configure Settings**: Click the settings icon (⚙️) in the header to set:
   - **Notion API Key**: Get this from your backend `.env` file
   - **Notion Database ID**: The ID of your tasks database

2. **Send Commands**: Use slash commands to interact with your Notion tasks:
   - `/task list` - List all tasks
   - `/task create title:"My task" priority:High` - Create a new task
   - `/task update task_id status:Done` - Update a task
   - `/task delete task_id` - Delete a task

### Command Syntax

Commands follow this pattern:
```
/task <action> [param1:value1] [param2:"value with spaces"]
```

**Key-value pairs:**
- Use `:` to separate key and value
- Use quotes for values with spaces: `title:"My task"`
- Optional parameters can be omitted

### Examples

```bash
# List tasks with filters
/task list status:open priority:High

# Create a task
/task create title:"Fix login bug" priority:High assignee_id:user_001

# Update a task status
/task update abc123def456 status:completed

# Delete a task
/task delete abc123def456
```

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API client and task API functions
│   ├── components/    # React components
│   │   ├── ui/        # shadcn/ui base components
│   │   ├── AuthModal.tsx
│   │   ├── ChatContainer.tsx
│   │   ├── CommandInput.tsx
│   │   ├── Message.tsx
│   │   ├── MessageList.tsx
│   │   └── TaskCard.tsx
│   ├── lib/           # Utilities
│   │   ├── apiMapper.ts      # Command to API request mapper
│   │   ├── commands.ts       # Command registry
│   │   ├── commandParser.ts  # Command parser
│   │   └── utils.ts          # General utilities
│   ├── store/         # State management
│   │   └── chatStore.ts      # Zustand store
│   ├── types/         # TypeScript types
│   │   ├── api.ts
│   │   ├── message.ts
│   │   └── task.ts
│   ├── App.tsx        # Main app component
│   ├── main.tsx       # Entry point
│   └── index.css      # Global styles
├── .env               # Environment variables (not committed)
├── .env.example       # Example environment variables
├── package.json       # Dependencies
├── tsconfig.json      # TypeScript configuration
├── tailwind.config.js # Tailwind configuration
└── vite.config.ts     # Vite configuration
```

## Available Commands

### Development
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

### Type Checking
- `npm run type-check` - Run TypeScript type checking (if script is added)

## Features

✅ **Implemented:**
- Real-time chat interface
- Slash command parsing
- Task creation, listing, updating, and deletion
- Formatted task display with cards
- Error handling with user-friendly messages
- Loading states and animations
- Responsive design
- Authentication via API key
- Session persistence

⏳ **In Progress:**
- Slash command autocomplete dropdown
- Command history (↑ arrow to recall)

🔮 **Future Enhancements:**
- Real-time task updates
- Multi-line input support
- Rich text formatting
- File attachments
- Collaborative features

## Troubleshooting

### CORS Errors
Make sure the backend `.env` file includes your frontend URL in `CORS_ORIGINS`:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000
```

### API Key Issues
- Ensure you're using the correct Notion API key from the backend
- Check that the API key has access to the specified database
- The key should be stored in sessionStorage (automatically handled)

### Build Failures
If you encounter build errors:
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Make sure you're using Node.js 18 or higher

### Frontend Not Serving
If accessing `http://localhost:8000/chat` returns 404:
1. Make sure you've built the frontend: `npm run build`
2. Check that `frontend/dist` directory exists
3. Restart the backend server

## Contributing

When adding new features:
1. Follow the existing code structure
2. Add TypeScript types for all new interfaces
3. Update this README with new commands/features
4. Test both development and production builds

## License

See main project LICENSE file.
