# Notion Bot API - Quick Reference

Quick reference for developers and operators working with the Notion Bot API.

## 🚀 Quick Start

```bash
# Start the API
docker-compose up -d

# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

## 📚 Documentation

| Document | Purpose | Location |
|----------|---------|----------|
| **API Documentation** | API endpoints, auth, rate limits, errors | [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) |
| **Notion Setup** | Create integration, get API key | [docs/NOTION_INTEGRATION_SETUP.md](docs/NOTION_INTEGRATION_SETUP.md) |
| **Deployment Guide** | Docker, K8s, cloud deployment | [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) |
| **Operations Runbook** | Troubleshooting, monitoring, backups | [docs/OPERATIONS_RUNBOOK.md](docs/OPERATIONS_RUNBOOK.md) |
| **Performance Testing** | Load testing, benchmarks | [tests/performance/README.md](tests/performance/README.md) |

## 🔍 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Metrics (Prometheus format)
```bash
curl http://localhost:8000/metrics
```

### Key Metrics
- `http_request_duration_seconds` - P50, P95, P99 latency
- `http_requests_total` - Request count by endpoint/status
- `notion_api_calls_total` - Total Notion API calls
- `rate_limit_hits_total` - Rate limit hits

### View Logs
```bash
docker-compose logs -f api
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/
```

### Performance Tests
```bash
./scripts/run_performance_tests.sh
```

### Integration Tests
```bash
pytest tests/integration/
```

## 🔧 Common Operations

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Restart API
```bash
docker-compose restart api
```

### View Resource Usage
```bash
docker stats notion-bot-api notion-bot-mongodb
```

### Access MongoDB
```bash
docker-compose exec mongodb mongosh notion_bot
```

## 🔑 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NOTION_API_KEY` | Yes | - | Notion integration API key |
| `NOTION_DATABASE_ID` | Yes | - | Notion database ID |
| `MONGODB_URI` | Yes | - | MongoDB connection string |
| `API_PORT` | No | 8000 | API port |
| `LOG_LEVEL` | No | INFO | Logging level |

## 📊 API Endpoints

### Core Endpoints
- `GET /` - API root
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

### Tasks
- `GET /tasks` - List tasks
- `POST /tasks` - Create task
- `GET /tasks/{id}` - Get task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task
- `POST /tasks/{id}/sync` - Sync with Notion

### Workspaces
- `GET /workspaces` - List workspaces
- `POST /workspaces` - Create workspace
- `GET /workspaces/{id}` - Get workspace
- `PUT /workspaces/{id}` - Update workspace
- `DELETE /workspaces/{id}` - Delete workspace

### Users
- `GET /users` - List users
- `POST /users` - Create user
- `GET /users/{id}` - Get user
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

## 🚨 Troubleshooting

### API Not Starting
```bash
# Check logs
docker-compose logs api

# Verify environment variables
docker-compose exec api env | grep NOTION

# Check port availability
lsof -i :8000
```

### Database Connection Issues
```bash
# Test MongoDB
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Check connection string
docker-compose exec api env | grep MONGODB_URI
```

### Notion API Issues
```bash
# Check Notion health
curl http://localhost:8000/health | jq '.checks.notion'

# Test API key
curl -H "Authorization: Bearer $NOTION_API_KEY" \
     https://api.notion.com/v1/databases
```

### High Latency
```bash
# Check metrics
curl http://localhost:8000/metrics | grep p95

# Check resource usage
docker stats

# Check rate limits
curl http://localhost:8000/metrics | grep rate_limit_hits
```

## 💾 Backup & Recovery

### Create Backup
```bash
docker-compose exec mongodb mongodump \
  --archive=/data/backup/backup.archive \
  --db=notion_bot \
  --gzip
```

### Restore Backup
```bash
docker-compose exec mongodb mongorestore \
  --archive=/data/backup/backup.archive \
  --db=notion_bot \
  --gzip \
  --drop
```

## 🔐 Security

### Best Practices
- ✅ Never commit `.env` files
- ✅ Use secrets management in production
- ✅ Enable HTTPS in production
- ✅ Restrict CORS origins
- ✅ Rotate API keys regularly
- ✅ Monitor for unusual activity

## 📈 Performance Targets

| Metric | Target | Description |
|--------|--------|-------------|
| **P95 Latency** | < 500ms | 95% of requests |
| **Availability** | > 99.9% | Uptime SLA |
| **Error Rate** | < 1% | Failed requests |
| **Throughput** | 100 req/s | Sustained load |

## 🔄 Rate Limits

- **Notion API**: ~3 requests/second per integration
- **Automatic Retry**: Exponential backoff (1s → 8s max)
- **Max Retries**: 4 retries (5 total attempts)

## 📞 Support

- **Documentation**: See `/docs` directory
- **Logs**: `docker-compose logs -f api`
- **Metrics**: http://localhost:8000/metrics
- **Health**: http://localhost:8000/health

## 🎯 Quick Checks

```bash
# Is the API healthy?
curl -f http://localhost:8000/health || echo "UNHEALTHY"

# What's the current load?
curl -s http://localhost:8000/metrics | grep http_requests_total | tail -5

# Any rate limit issues?
curl -s http://localhost:8000/metrics | grep rate_limit_hits_total

# How's the latency?
curl -s http://localhost:8000/metrics | grep 'quantile="0.95"'
```

## 🛠️ Development

### Run Locally (without Docker)
```bash
# Install dependencies
poetry install

# Set environment variables
export NOTION_API_KEY=secret_...
export MONGODB_URI=mongodb://localhost:27017

# Run API
poetry run python -m src.main
```

### Code Quality
```bash
# Format code
poetry run black src/ tests/

# Lint code
poetry run ruff src/ tests/

# Type checking
poetry run mypy src/
```

## 📖 Additional Resources

- [Notion API Docs](https://developers.notion.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [MongoDB Docs](https://docs.mongodb.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)

---

For detailed information, see the full documentation in the `docs/` directory.
