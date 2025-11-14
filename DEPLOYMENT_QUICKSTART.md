# Notion Bot API - Quick Deployment Guide

This guide provides straightforward steps to deploy the Notion Bot API in different environments, addressing common deployment challenges.

## 🚀 Quick Start (Local Development)

### Prerequisites
- **Docker** and **Docker Compose** 
- **Python 3.11+** (only if running locally without Docker)
- **Notion Integration Token** (get from [Notion Integrations](https://www.notion.so/my-integrations))

### Step-by-step Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd notion-bot
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env and set your NOTION_API_KEY
```

3. **(Alternative 1) Deploy with Docker Compose (Recommended):**
```bash
# Start both MongoDB and the API application
docker-compose up -d

# Check if services are running
docker-compose ps

# View application logs
docker-compose logs -f app
```

4. **(Alternative 2) Run without Docker (if Docker Compose fails):**
```bash
# Start MongoDB with Docker (if you have Docker)
docker run -d --name notion-bot-mongodb -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password123 \
  -e MONGO_INITDB_DATABASE=notion-bot \
  mongo:7.0

# Install dependencies
pip install -r requirements.txt

# Run the application (set PYTHONPATH to allow module imports)
PYTHONPATH=. python -c "
import uvicorn
from src.main import app
from src.config.settings import get_settings

settings = get_settings()
print(f'Starting server on {settings.api_host}:{settings.api_port}')
uvicorn.run(app, host=settings.api_host, port=settings.api_port, reload=settings.debug, log_level='info')
"
```

5. **Verify the API is running:**
```bash
curl http://localhost:8000/health
```

The expected response should be:
```json
{
  "status": "healthy",
  "checks": {
    "database": {
      "status": "healthy",
      "mongodb": {
        "status": "connected",
        "ping": {
          "ok": 1.0
        }
      }
    }
  }
}
```

## 🏗️ Environment Configuration

### Required Variables
| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB connection string |
| `NOTION_API_KEY` | Your Notion integration token |

### Common Configuration Issues & Solutions

**Issue:** `services.app.environment.NOTION_API_VERSION invalid jsonType time.Time`
- **Solution:** Make sure your `docker-compose.yml` file is valid YAML. If you encounter this error, use the manual Docker method above instead.

**Issue:** `ModuleNotFoundError: No module named 'src'`
- **Solution:** Run with `PYTHONPATH=.` prefix to make Python recognize the `src` module.

**Issue:** Docker Compose validation errors
- **Solution:** Use individual Docker commands as shown in the alternative setup above.

## 🌐 Production Deployment

### Using Docker Compose (Production Mode)

1. **Create production environment file:**
```bash
cp .env.example .env.prod
# Edit .env.prod with production settings
```

2. **Deploy using production compose file:**
```bash
# Build and start in production mode
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### Using MongoDB Atlas (Recommended for Production)

1. **Update your environment file with MongoDB Atlas connection string:**
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/notion-bot?retryWrites=true&w=majority
```

2. **Deploy without MongoDB service:**
```bash
# This will only start the app service, connecting to your Atlas instance
docker-compose -f docker-compose.prod.yml up -d app
```

## 🔧 Common Troubleshooting

### Issue: Container won't start
**Check:**
- Valid `NOTION_API_KEY` in your `.env` file
- MongoDB is healthy before starting the app
- Port 8000 is not already in use

**Commands to debug:**
```bash
# Check logs
docker-compose logs app

# If running without Docker Compose, ensure PYTHONPATH is set
PYTHONPATH=. python src/main.py
```

### Issue: MongoDB connection failures
**Verify:**
- MongoDB container is running: `docker ps | grep mongo`
- Credentials in `.env` match MongoDB setup
- Connection string format is correct

### Issue: API not responding
**Check:**
- MongoDB is accessible and running
- Notion API key is valid
- Application is starting without errors (check logs)

## 📊 Health Checks

Verify API health with:
```bash
curl http://localhost:8000/health

# For a complete check:
curl http://localhost:8000/
curl http://localhost:8000/docs  # API documentation
```

## 🛠️ Running Tests

Before deployment, run the test suite:
```bash
# Unit tests
python -m pytest tests/unit/ -v

# If you want to run without Docker
PYTHONPATH=. python -m pytest tests/unit/ -v
```

## 🚢 Deployment Checklist

- [ ] Valid Notion API key configured
- [ ] MongoDB is accessible (local Docker or Atlas)
- [ ] Environment variables set appropriately
- [ ] All tests pass
- [ ] Health check endpoint responds properly
- [ ] CORS settings configured for your domain
- [ ] Security settings appropriate for environment (DEBUG disabled in production)

## 📞 Support

If you encounter deployment issues not covered in this guide:

1. Check application logs: `docker-compose logs app`
2. Verify environment: `docker-compose config`
3. Review the main [DEPLOYMENT.md](DEPLOYMENT.md) for more detailed information
4. Test with the API documentation: `http://localhost:8000/docs`