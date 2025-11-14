# Deployment Guide

Complete guide for deploying Notion Bot API to various environments.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Health Checks & Monitoring](#health-checks--monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Backup & Recovery](#backup--recovery)

---

## Prerequisites

### Required
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Python** 3.11+ (for local development)
- **Notion Integration Token** (from https://www.notion.so/my-integrations)
- **Notion Database ID** (from your Notion workspace)

### Optional
- **MongoDB Atlas** account (for production)
- **Reverse proxy** (nginx, Traefik) for SSL/TLS
- **Monitoring tools** (Prometheus, Grafana)

---

## Local Development

### Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd notion-bot

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and set NOTION_API_KEY

# 5. Start MongoDB
docker-compose up -d mongodb

# 6. Run application
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Points
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Docker Deployment

### Development Mode

Use the automated deployment script:

```bash
./deploy.sh
```

Or manually:

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your NOTION_API_KEY

# 2. Build and start
docker-compose up -d --build

# 3. Check status
docker-compose ps
docker-compose logs -f app

# 4. Verify health
curl http://localhost:8000/health
```

### Stop Services

```bash
docker-compose down
# To also remove volumes:
docker-compose down -v
```

---

## Production Deployment

### Using Docker Compose (Production Mode)

```bash
# 1. Create production environment file
cat > .env.prod <<EOF
# MongoDB
MONGO_USERNAME=admin
MONGO_PASSWORD=$(openssl rand -base64 32)

# Notion API
NOTION_API_KEY=secret_your_actual_token_here

# CORS - Update with your actual domain
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Logging
LOG_LEVEL=WARNING
EOF

# 2. Deploy with production compose file
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# 3. Check logs
docker-compose -f docker-compose.prod.yml logs -f

# 4. Verify deployment
curl https://yourdomain.com/health
```

### Using MongoDB Atlas (Recommended for Production)

```bash
# Update .env.prod
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/notion-bot?retryWrites=true&w=majority

# Deploy without MongoDB service
docker-compose -f docker-compose.prod.yml up -d app
```

### Behind Reverse Proxy (nginx)

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to API
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint (for load balancer)
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

---

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/notion-bot` |
| `NOTION_API_KEY` | Notion integration token | `secret_xxxxxxxxxxxxx` |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTION_API_VERSION` | `2022-10-28` | Notion API version |
| `API_HOST` | `0.0.0.0` | API bind address |
| `API_PORT` | `8000` | API port |
| `DEBUG` | `false` | Debug mode |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins (comma-separated) |

### Security Best Practices

**❌ Never:**
- Commit `.env` files to version control
- Use default passwords in production
- Expose MongoDB port publicly
- Use `DEBUG=true` in production

**✅ Always:**
- Use strong passwords (32+ characters)
- Enable SSL/TLS for production
- Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- Regularly rotate credentials
- Set restrictive CORS origins

---

## Health Checks & Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "mongodb": {
      "status": "connected",
      "latency_ms": 5
    },
    "notion_api": {
      "status": "connected"
    }
  }
}
```

### Docker Health Checks

Built-in health checks are configured in docker-compose:
- **MongoDB**: Checks every 10s
- **API**: Checks every 30s

View health status:
```bash
docker-compose ps
docker inspect notion-bot-api | grep -A 5 Health
```

### Logging

View application logs:
```bash
# All logs
docker-compose logs -f

# Only API logs
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app

# With timestamps
docker-compose logs -f -t app
```

### Monitoring Endpoints

**Planned** (not yet implemented):
- `/metrics` - Prometheus metrics
- Request count, latency, error rate
- Notion API call metrics

---

## Troubleshooting

### Common Issues

#### 1. Container won't start

```bash
# Check logs
docker-compose logs app

# Common causes:
# - Missing NOTION_API_KEY in .env
# - MongoDB not healthy
# - Port 8000 already in use
```

#### 2. MongoDB connection failed

```bash
# Check MongoDB is running
docker-compose ps mongodb

# Check MongoDB logs
docker-compose logs mongodb

# Test connection
docker exec -it notion-bot-mongodb mongosh --eval "db.adminCommand('ping')"

# Verify credentials in .env match docker-compose.yml
```

#### 3. Notion API errors

```bash
# Verify API key is valid
curl -H "Authorization: Bearer $NOTION_API_KEY" \
     -H "Notion-Version: 2022-10-28" \
     https://api.notion.com/v1/users/me

# Check API key has database access
# The integration must be added as a connection to your database in Notion
```

#### 4. CORS errors

```bash
# Update CORS_ORIGINS in .env
CORS_ORIGINS=https://yourfrontend.com,https://www.yourfrontend.com

# Restart container
docker-compose restart app
```

#### 5. Rate limit exceeded

The API handles Notion rate limits automatically with exponential backoff.

Check logs for rate limit warnings:
```bash
docker-compose logs app | grep "rate_limit"
```

### Debug Mode

Enable debug logging:
```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart
docker-compose restart app
```

---

## Backup & Recovery

### MongoDB Backup

#### Manual Backup

```bash
# Create backup directory
mkdir -p mongodb-backup

# Backup database
docker exec notion-bot-mongodb mongodump \
  --username admin \
  --password password123 \
  --authenticationDatabase admin \
  --db notion-bot \
  --out /backup/$(date +%Y%m%d_%H%M%S)

# Copy from container to host
docker cp notion-bot-mongodb:/backup ./mongodb-backup/
```

#### Automated Backup Script

```bash
#!/bin/bash
# backup-mongodb.sh

BACKUP_DIR="./mongodb-backup"
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"

# Create backup
docker exec notion-bot-mongodb mongodump \
  --username admin \
  --password password123 \
  --authenticationDatabase admin \
  --db notion-bot \
  --out /backup/$BACKUP_NAME

# Copy to host
docker cp notion-bot-mongodb:/backup/$BACKUP_NAME $BACKUP_DIR/

# Keep only last 7 backups
ls -t $BACKUP_DIR/backup_* | tail -n +8 | xargs rm -rf

echo "Backup completed: $BACKUP_DIR/$BACKUP_NAME"
```

#### Restore from Backup

```bash
# Copy backup to container
docker cp ./mongodb-backup/backup_20250114_120000 notion-bot-mongodb:/backup/

# Restore database
docker exec notion-bot-mongodb mongorestore \
  --username admin \
  --password password123 \
  --authenticationDatabase admin \
  --db notion-bot \
  --drop \
  /backup/backup_20250114_120000/notion-bot
```

### Disaster Recovery

#### Complete System Restore

```bash
# 1. Restore MongoDB backup (see above)

# 2. Verify environment configuration
cat .env

# 3. Restart services
docker-compose down
docker-compose up -d

# 4. Verify health
curl http://localhost:8000/health
```

---

## Performance Optimization

### Resource Limits

Production deployment includes resource limits:
- **CPU**: 2 cores max, 0.5 reserved
- **Memory**: 1GB max, 512MB reserved

Adjust in `docker-compose.prod.yml` if needed.

### Scaling

#### Horizontal Scaling

For high traffic, run multiple API instances:

```bash
# Scale to 3 instances
docker-compose up -d --scale app=3

# Use load balancer (nginx, HAProxy) to distribute traffic
```

#### Database Optimization

- Use MongoDB Atlas for managed, auto-scaling database
- Enable connection pooling (already configured)
- Create indexes on frequently queried fields (see `init-mongo.js`)

---

## Production Checklist

Before going live:

- [ ] Set strong passwords for MongoDB
- [ ] Configure valid NOTION_API_KEY
- [ ] Set restrictive CORS_ORIGINS
- [ ] Set LOG_LEVEL=WARNING
- [ ] Set DEBUG=false
- [ ] Enable SSL/TLS (HTTPS)
- [ ] Set up monitoring and alerts
- [ ] Configure automated backups
- [ ] Test disaster recovery procedure
- [ ] Load test the API
- [ ] Review security headers
- [ ] Document incident response procedures

---

## Support

For issues and questions:
- Check [GitHub Issues](https://github.com/yourusername/notion-bot/issues)
- Review [API Documentation](http://localhost:8000/docs)
- Check application logs

---

**Last Updated:** 2025-01-14
