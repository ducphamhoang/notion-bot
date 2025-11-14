# Notion Bot API Deployment Scripts

This directory contains automated deployment scripts for the Notion Bot API to simplify the deployment process.

## Available Scripts

### Linux/macOS: `deploy.sh`
A bash script for deploying the Notion Bot API on Linux and macOS systems.

### Windows: `deploy.ps1`
A PowerShell script for deploying the Notion Bot API on Windows systems.

## Prerequisites

Before using these scripts, ensure you have:

- Docker and Docker Compose installed
- Git (for cloning the repository)
- Internet access to pull required images

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd notion-bot
```

2. Create your environment file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your Notion API key:
```bash
NOTION_API_KEY=secret_your_notion_integration_token_here
```

## Using the Deployment Scripts

### On Linux/macOS:
```bash
# Deploy in development mode (default)
./deploy.sh

# Deploy in production mode
./deploy.sh -e prod

# View help
./deploy.sh -h

# View logs
./deploy.sh --logs

# Check status
./deploy.sh --status

# Stop services
./deploy.sh --stop

# Restart services
./deploy.sh --restart
```

### On Windows:
```powershell
# Deploy in development mode (default)
.\deploy.ps1

# Deploy in production mode
.\deploy.ps1 -e prod

# View logs
.\deploy.ps1 --logs

# Check status
.\deploy.ps1 --status

# Stop services
.\deploy.ps1 --stop

# Restart services
.\deploy.ps1 --restart
```

## Configuration

The scripts support two environments:

- `dev` (default): Uses `docker-compose.yml` for development
- `prod`: Uses `docker-compose.prod.yml` for production

For production deployments, you'll need to create `.env.prod` with production settings.

## Features

- Automatic prerequisite checking
- Environment validation
- Service startup with health checks
- Deployment verification
- Status monitoring
- Log viewing
- Service management (stop, restart)

## Troubleshooting

If the deployment fails:

1. Check that Docker and Docker Compose are installed and running
2. Verify your `.env` file has the correct configuration
3. Review the script output for specific error messages
4. Check that ports 8000 and 27017 are available
5. Ensure your Notion API key has the correct permissions