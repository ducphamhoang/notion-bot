# Deployment Guide

This guide provides step-by-step instructions for deploying the Notion Bot API in various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Production Deployment](#production-deployment)
  - [Using Docker Compose](#using-docker-compose)
  - [Using Kubernetes](#using-kubernetes)
  - [Cloud Deployment (AWS/GCP/Azure)](#cloud-deployment)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Health Checks & Monitoring](#health-checks--monitoring)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

1. **Notion Integration** configured (see [Notion Integration Setup](./NOTION_INTEGRATION_SETUP.md))
2. **MongoDB** instance (local or cloud-hosted)
3. **Docker** (version 20.10+) and **Docker Compose** (version 2.0+)
4. **Environment variables** configured (`.env` file or secrets management)

### Minimum System Requirements

- **CPU**: 2 cores
- **RAM**: 2 GB
- **Storage**: 10 GB (for application and logs)
- **Network**: Outbound HTTPS access to Notion API and MongoDB

---

## Quick Start (Docker)

For local development or testing:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd notion-bot
```

### 2. Configure Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Notion Configuration
NOTION_API_KEY=secret_your_notion_api_key_here
NOTION_DATABASE_ID=your_database_id_here

# MongoDB Configuration
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DB_NAME=notion_bot

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 3. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### 4. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# API root
curl http://localhost:8000/

# View metrics
curl http://localhost:8000/metrics
```

### 5. Stop Services

```bash
docker-compose down

# To also remove volumes (database data):
docker-compose down -v
```

---

## Production Deployment

### Using Docker Compose

#### 1. Prepare Production Environment

Create a `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    image: notion-bot-api:latest
    container_name: notion-bot-api
    restart: always
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - DEBUG=false
      - LOG_LEVEL=INFO
      - MONGODB_URI=mongodb://mongodb:27017
      - MONGODB_DB_NAME=notion_bot
      - NOTION_API_KEY=${NOTION_API_KEY}
      - NOTION_DATABASE_ID=${NOTION_DATABASE_ID}
      - CORS_ORIGINS=${CORS_ORIGINS}
    depends_on:
      - mongodb
    networks:
      - notion-bot-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  mongodb:
    image: mongo:7.0
    container_name: notion-bot-mongodb
    restart: always
    volumes:
      - mongodb_data:/data/db
      - mongodb_logs:/var/log/mongodb
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGO_ROOT_USERNAME}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_ROOT_PASSWORD}
    networks:
      - notion-bot-network
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: notion-bot-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - notion-bot-network

volumes:
  mongodb_data:
    driver: local
  mongodb_logs:
    driver: local

networks:
  notion-bot-network:
    driver: bridge
```

#### 2. Configure Production Environment

Create `.env.prod`:

```env
# Production configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
LOG_LEVEL=WARNING

# Notion (use secrets management in production)
NOTION_API_KEY=secret_production_key
NOTION_DATABASE_ID=production_database_id

# MongoDB with authentication
MONGODB_URI=mongodb://admin:secure_password@mongodb:27017/notion_bot?authSource=admin
MONGODB_DB_NAME=notion_bot
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=secure_password

# CORS (whitelist production domains only)
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

#### 3. Deploy

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Verify health
curl https://yourdomain.com/health
```

#### 4. Setup Nginx (Optional)

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        listen 80;
        server_name yourdomain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000" always;

        location / {
            limit_req zone=api_limit burst=20 nodelay;

            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /health {
            proxy_pass http://api/health;
            access_log off;
        }

        location /metrics {
            # Restrict access to monitoring systems
            allow 10.0.0.0/8;  # Internal network
            deny all;

            proxy_pass http://api/metrics;
        }
    }
}
```

---

### Using Kubernetes

#### 1. Create Kubernetes Manifests

**Namespace** (`namespace.yaml`):

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: notion-bot
```

**ConfigMap** (`configmap.yaml`):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: notion-bot-config
  namespace: notion-bot
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  MONGODB_URI: "mongodb://mongodb:27017"
  MONGODB_DB_NAME: "notion_bot"
  CORS_ORIGINS: "https://yourdomain.com"
```

**Secret** (`secret.yaml`):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: notion-bot-secrets
  namespace: notion-bot
type: Opaque
stringData:
  NOTION_API_KEY: "secret_your_key_here"
  NOTION_DATABASE_ID: "your_database_id"
```

**Deployment** (`deployment.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notion-bot-api
  namespace: notion-bot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: notion-bot-api
  template:
    metadata:
      labels:
        app: notion-bot-api
    spec:
      containers:
      - name: api
        image: notion-bot-api:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: notion-bot-config
        - secretRef:
            name: notion-bot-secrets
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

**Service** (`service.yaml`):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: notion-bot-api
  namespace: notion-bot
spec:
  type: LoadBalancer
  selector:
    app: notion-bot-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

#### 2. Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check status
kubectl get pods -n notion-bot
kubectl get svc -n notion-bot

# View logs
kubectl logs -n notion-bot -l app=notion-bot-api -f

# Check health
kubectl exec -n notion-bot -it <pod-name> -- curl localhost:8000/health
```

---

### Cloud Deployment

#### AWS (Elastic Container Service)

1. **Build and push Docker image to ECR**:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t notion-bot-api .
docker tag notion-bot-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/notion-bot-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/notion-bot-api:latest
```

2. **Create ECS Task Definition** with environment variables from AWS Secrets Manager

3. **Deploy to ECS** using Fargate or EC2 launch type

4. **Configure Application Load Balancer** with health check on `/health`

#### Google Cloud Platform (Cloud Run)

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/<project-id>/notion-bot-api
gcloud run deploy notion-bot-api \
  --image gcr.io/<project-id>/notion-bot-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NOTION_API_KEY=<key>,MONGODB_URI=<uri>
```

#### Azure (Container Instances)

```bash
az container create \
  --resource-group notion-bot-rg \
  --name notion-bot-api \
  --image notion-bot-api:latest \
  --cpu 2 --memory 2 \
  --ports 8000 \
  --environment-variables \
    NOTION_API_KEY=<key> \
    MONGODB_URI=<uri>
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_HOST` | No | `0.0.0.0` | API host binding |
| `API_PORT` | No | `8000` | API port |
| `DEBUG` | No | `false` | Enable debug mode |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `NOTION_API_KEY` | Yes | - | Notion integration API key |
| `NOTION_DATABASE_ID` | Yes | - | Notion database ID for tasks |
| `MONGODB_URI` | Yes | - | MongoDB connection string |
| `MONGODB_DB_NAME` | Yes | - | MongoDB database name |
| `CORS_ORIGINS` | No | `*` | Comma-separated allowed origins |

### Secrets Management (Production)

**Never store secrets in code or plain text files in production.**

Use:
- **AWS**: Secrets Manager or Parameter Store
- **GCP**: Secret Manager
- **Azure**: Key Vault
- **Kubernetes**: Kubernetes Secrets
- **Docker**: Docker Secrets
- **HashiCorp Vault**: For any environment

---

## Database Setup

### MongoDB Atlas (Recommended for Production)

1. Create a MongoDB Atlas cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Configure network access (IP whitelist)
3. Create database user with read/write permissions
4. Get connection string:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/notion_bot?retryWrites=true&w=majority
   ```
5. Set `MONGODB_URI` environment variable

### Self-Hosted MongoDB

If using Docker Compose (included in `docker-compose.prod.yml`):

```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh

# Create database and user
use notion_bot
db.createUser({
  user: "notion_bot_user",
  pwd: "secure_password",
  roles: [{role: "readWrite", db: "notion_bot"}]
})
```

---

## Health Checks & Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy"},
    "notion": {"status": "healthy"}
  }
}
```

### Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

### Prometheus Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'notion-bot-api'
    scrape_interval: 15s
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
```

### Grafana Dashboard

Import dashboard or create panels for:
- Request duration percentiles (P50, P95, P99)
- HTTP status codes distribution
- Notion API call rate
- Rate limit hits

---

## Troubleshooting

See the [Operations Runbook](./OPERATIONS_RUNBOOK.md) for:
- Common deployment issues
- Debugging steps
- Performance tuning
- Disaster recovery

### Quick Checks

1. **Container logs**:
   ```bash
   docker-compose logs -f api
   ```

2. **Health check**:
   ```bash
   curl http://localhost:8000/health
   ```

3. **Database connectivity**:
   ```bash
   docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
   ```

4. **Notion API connectivity**:
   ```bash
   curl http://localhost:8000/health | jq '.checks.notion'
   ```

---

## Next Steps

After successful deployment:

1. **Set up monitoring** - Configure Prometheus/Grafana
2. **Configure backups** - See [Operations Runbook](./OPERATIONS_RUNBOOK.md#backup-procedures)
3. **Set up alerts** - For downtime, errors, performance degradation
4. **Load testing** - Verify performance under load
5. **Security hardening** - Review and apply security best practices

---

## Support

For deployment issues:

1. Check logs for detailed error messages
2. Review [Operations Runbook](./OPERATIONS_RUNBOOK.md)
3. Verify all prerequisites are met
4. Contact your DevOps team or system administrator
