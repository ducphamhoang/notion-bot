# Operations Runbook

This runbook provides operational procedures for managing and troubleshooting the Notion Bot API in production.

## Table of Contents

- [Common Issues](#common-issues)
- [Monitoring System Health](#monitoring-system-health)
- [Backup and Recovery Procedures](#backup-and-recovery-procedures)
- [Handling Notion API Rate Limits](#handling-notion-api-rate-limits)
- [Performance Tuning](#performance-tuning)
- [Incident Response](#incident-response)
- [Maintenance Procedures](#maintenance-procedures)

---

## Common Issues

### Issue 1: API Returns 503 (Service Unavailable)

**Symptoms**:
- Health check endpoint returns 503 status
- Application logs show connection errors

**Common Causes**:
1. Database connection failure
2. Notion API connectivity issues
3. Application startup failure

**Troubleshooting Steps**:

1. **Check health endpoint**:
   ```bash
   curl -v http://localhost:8000/health
   ```

2. **Inspect the response** to identify which component is unhealthy:
   ```json
   {
     "status": "unhealthy",
     "checks": {
       "database": {"status": "unhealthy", "error": "Connection refused"},
       "notion": {"status": "healthy"}
     }
   }
   ```

3. **Database issues**:
   ```bash
   # Check MongoDB is running
   docker-compose ps mongodb
   
   # Check MongoDB logs
   docker-compose logs mongodb
   
   # Test connection manually
   docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
   
   # Verify connection string in environment
   docker-compose exec api env | grep MONGODB_URI
   ```

4. **Notion API issues**:
   ```bash
   # Check Notion API status
   curl https://status.notion.so/api/v2/status.json
   
   # Test API key manually
   curl -H "Authorization: Bearer $NOTION_API_KEY" \
        -H "Notion-Version: 2022-06-28" \
        https://api.notion.com/v1/databases
   
   # Check application logs for Notion errors
   docker-compose logs api | grep -i "notion"
   ```

5. **Application startup issues**:
   ```bash
   # Check container status
   docker-compose ps
   
   # View full application logs
   docker-compose logs -f api
   
   # Restart the service
   docker-compose restart api
   ```

**Resolution**:
- Fix database connectivity (check URI, credentials, network)
- Verify Notion API key is valid and has correct permissions
- Check database is shared with the Notion integration
- Restart services if transient issue

---

### Issue 2: High Latency / Slow Response Times

**Symptoms**:
- Requests take > 1 second to complete
- P95 latency > 500ms
- Timeout errors

**Common Causes**:
1. Database query performance issues
2. Notion API rate limiting
3. Resource constraints (CPU/memory)
4. Network issues

**Troubleshooting Steps**:

1. **Check metrics**:
   ```bash
   curl http://localhost:8000/metrics | grep http_request_duration_seconds
   ```

2. **Identify slow endpoints**:
   ```bash
   # Look for P95/P99 values > 0.5 seconds
   curl http://localhost:8000/metrics | grep -A 5 "http_request_duration_seconds"
   ```

3. **Check resource usage**:
   ```bash
   # Docker stats
   docker stats notion-bot-api notion-bot-mongodb
   
   # System resources
   top
   free -h
   df -h
   ```

4. **Check database performance**:
   ```bash
   # MongoDB slow queries
   docker-compose exec mongodb mongosh
   
   > use notion_bot
   > db.setProfilingLevel(2)  # Enable profiling
   > db.system.profile.find().sort({ts:-1}).limit(10).pretty()
   ```

5. **Check Notion API rate limits**:
   ```bash
   # Check rate limit hits
   curl http://localhost:8000/metrics | grep rate_limit_hits_total
   
   # Check application logs for rate limit errors
   docker-compose logs api | grep -i "rate"
   ```

**Resolution**:
- Add database indexes for frequently queried fields
- Scale up resources (CPU/memory)
- Implement caching for frequently accessed data
- Reduce Notion API call frequency
- Consider horizontal scaling (multiple API instances)

---

### Issue 3: Tasks Not Syncing with Notion

**Symptoms**:
- Tasks created in API don't appear in Notion
- Updates to tasks not reflected in Notion
- Sync errors in logs

**Common Causes**:
1. Notion database not shared with integration
2. Invalid database ID
3. Notion API errors
4. Task schema mismatch

**Troubleshooting Steps**:

1. **Check task in database**:
   ```bash
   docker-compose exec mongodb mongosh
   
   > use notion_bot
   > db.tasks.findOne({_id: ObjectId("task_id")})
   ```

2. **Manually trigger sync**:
   ```bash
   curl -X POST http://localhost:8000/tasks/{task_id}/sync
   ```

3. **Check Notion database access**:
   - Open Notion database
   - Click "..." menu → "Connections"
   - Verify your integration is listed

4. **Verify database ID**:
   ```bash
   docker-compose exec api env | grep NOTION_DATABASE_ID
   ```

5. **Check Notion API errors**:
   ```bash
   docker-compose logs api | grep -A 5 "notion.*error"
   ```

6. **Test Notion API directly**:
   ```bash
   curl -X POST https://api.notion.com/v1/pages \
     -H "Authorization: Bearer $NOTION_API_KEY" \
     -H "Notion-Version: 2022-06-28" \
     -H "Content-Type: application/json" \
     -d '{
       "parent": {"database_id": "'"$NOTION_DATABASE_ID"'"},
       "properties": {
         "Name": {"title": [{"text": {"content": "Test"}}]}
       }
     }'
   ```

**Resolution**:
- Share database with integration in Notion
- Update database ID if incorrect
- Fix task schema to match Notion database properties
- Check Notion API key permissions

---

### Issue 4: Container Keeps Restarting

**Symptoms**:
- Container status shows repeated restarts
- Application fails to start
- Health checks fail immediately

**Common Causes**:
1. Configuration errors
2. Missing required environment variables
3. Port conflicts
4. Application code errors

**Troubleshooting Steps**:

1. **Check container status**:
   ```bash
   docker-compose ps
   docker inspect notion-bot-api
   ```

2. **View container logs**:
   ```bash
   # Recent logs
   docker-compose logs --tail=100 api
   
   # Follow logs in real-time
   docker-compose logs -f api
   ```

3. **Check environment variables**:
   ```bash
   docker-compose exec api env
   ```

4. **Verify configuration**:
   ```bash
   # Check .env file
   cat .env
   
   # Validate docker-compose.yml
   docker-compose config
   ```

5. **Check port availability**:
   ```bash
   # See what's using port 8000
   sudo lsof -i :8000
   netstat -tuln | grep 8000
   ```

6. **Try running container interactively**:
   ```bash
   docker-compose run --rm api /bin/bash
   
   # Inside container
   python -m src.main
   ```

**Resolution**:
- Fix missing/invalid environment variables
- Resolve port conflicts
- Fix application code errors
- Check file permissions and volumes

---

## Monitoring System Health

### Daily Health Checks

Perform these checks daily (automate if possible):

1. **API Health**:
   ```bash
   curl -f http://localhost:8000/health || echo "ALERT: API unhealthy"
   ```

2. **Database Health**:
   ```bash
   docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')" || echo "ALERT: MongoDB down"
   ```

3. **Notion Connectivity**:
   ```bash
   curl http://localhost:8000/health | jq -e '.checks.notion.status == "healthy"' || echo "ALERT: Notion API issue"
   ```

4. **Disk Space**:
   ```bash
   df -h | grep -E '(Filesystem|/data|/var)' 
   
   # Alert if > 80% used
   df -h | awk '$5+0 > 80 {print "ALERT: " $0}'
   ```

5. **Memory Usage**:
   ```bash
   free -h
   
   # Alert if available < 500MB
   free -m | awk 'NR==2 {if ($7 < 500) print "ALERT: Low memory"}'
   ```

### Metrics to Monitor

Access metrics at: `http://localhost:8000/metrics`

**Key Metrics**:

1. **Request Duration** (target: P95 < 500ms):
   ```bash
   curl -s http://localhost:8000/metrics | grep 'quantile="0.95"'
   ```

2. **Error Rate** (target: < 1%):
   ```bash
   # Count 5xx errors
   curl -s http://localhost:8000/metrics | grep 'status_code="5' | awk '{sum+=$2} END {print sum}'
   ```

3. **Notion API Calls** (monitor rate):
   ```bash
   curl -s http://localhost:8000/metrics | grep notion_api_calls_total
   ```

4. **Rate Limit Hits** (target: 0):
   ```bash
   curl -s http://localhost:8000/metrics | grep rate_limit_hits_total
   ```

### Setting Up Alerts

**Prometheus Alert Rules** (`alerts.yml`):

```yaml
groups:
  - name: notion_bot_alerts
    interval: 30s
    rules:
      - alert: APIDown
        expr: up{job="notion-bot-api"} == 0
        for: 2m
        annotations:
          summary: "Notion Bot API is down"
          
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.01
        for: 5m
        annotations:
          summary: "High error rate detected"
          
      - alert: HighLatency
        expr: http_request_duration_seconds{quantile="0.95"} > 0.5
        for: 10m
        annotations:
          summary: "API latency is high (P95 > 500ms)"
          
      - alert: RateLimitHits
        expr: increase(rate_limit_hits_total[1h]) > 10
        annotations:
          summary: "Notion API rate limit being hit frequently"
```

### Monitoring Dashboard

Grafana panels to create:

1. **API Health Overview**:
   - System status (up/down)
   - Request rate (req/s)
   - Error rate (%)
   - P50/P95/P99 latency

2. **Resource Usage**:
   - CPU usage (%)
   - Memory usage (%)
   - Disk usage (%)
   - Network I/O

3. **Notion API**:
   - API calls per minute
   - Rate limit hits
   - API error rate
   - Response times

4. **Database**:
   - Connection pool usage
   - Query latency
   - Operations per second
   - Storage usage

---

## Backup and Recovery Procedures

### MongoDB Backup

#### Automated Daily Backup

Create backup script (`scripts/backup.sh`):

```bash
#!/bin/bash
set -e

BACKUP_DIR="/backup/mongodb"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="notion_bot_backup_${TIMESTAMP}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Run mongodump
docker-compose exec -T mongodb mongodump \
  --archive="/data/backup/${BACKUP_NAME}.archive" \
  --db=notion_bot \
  --gzip

# Copy to host
docker cp notion-bot-mongodb:/data/backup/${BACKUP_NAME}.archive ${BACKUP_DIR}/

# Remove old backups (keep last 7 days)
find ${BACKUP_DIR} -name "*.archive" -mtime +7 -delete

echo "Backup completed: ${BACKUP_NAME}.archive"
```

Schedule with cron:

```bash
# Daily backup at 2 AM
0 2 * * * /path/to/scripts/backup.sh >> /var/log/notion-bot-backup.log 2>&1
```

#### Manual Backup

```bash
# Create backup
docker-compose exec mongodb mongodump \
  --archive=/data/backup/manual_backup.archive \
  --db=notion_bot \
  --gzip

# Copy to host
docker cp notion-bot-mongodb:/data/backup/manual_backup.archive ./backup/
```

#### Backup to Cloud Storage

**AWS S3**:

```bash
#!/bin/bash
BACKUP_FILE="notion_bot_backup_$(date +%Y%m%d).archive"

# Create backup
docker-compose exec -T mongodb mongodump --archive --gzip > ${BACKUP_FILE}

# Upload to S3
aws s3 cp ${BACKUP_FILE} s3://your-backup-bucket/notion-bot/

# Clean up local file
rm ${BACKUP_FILE}
```

**Google Cloud Storage**:

```bash
#!/bin/bash
BACKUP_FILE="notion_bot_backup_$(date +%Y%m%d).archive"

# Create backup
docker-compose exec -T mongodb mongodump --archive --gzip > ${BACKUP_FILE}

# Upload to GCS
gsutil cp ${BACKUP_FILE} gs://your-backup-bucket/notion-bot/

# Clean up local file
rm ${BACKUP_FILE}
```

### MongoDB Recovery

#### Restore from Backup

```bash
# Stop the API (to prevent writes during restore)
docker-compose stop api

# Restore database
docker-compose exec -T mongodb mongorestore \
  --archive=/data/backup/notion_bot_backup_20231115.archive \
  --db=notion_bot \
  --gzip \
  --drop

# Restart API
docker-compose start api

# Verify restore
docker-compose exec mongodb mongosh notion_bot --eval "db.tasks.countDocuments()"
```

#### Point-in-Time Recovery

If using MongoDB Atlas with point-in-time backups:

1. Go to Atlas console
2. Select cluster → Backup tab
3. Choose "Restore" for desired snapshot
4. Select target cluster or download

#### Disaster Recovery Procedure

1. **Stop all services**:
   ```bash
   docker-compose down
   ```

2. **Restore database from latest backup**:
   ```bash
   # Copy backup file to MongoDB data directory
   docker-compose up -d mongodb
   
   docker cp backup/latest.archive notion-bot-mongodb:/data/backup/
   
   docker-compose exec mongodb mongorestore \
     --archive=/data/backup/latest.archive \
     --gzip \
     --drop
   ```

3. **Start API**:
   ```bash
   docker-compose up -d api
   ```

4. **Verify system health**:
   ```bash
   curl http://localhost:8000/health
   ```

5. **Check data integrity**:
   ```bash
   # Verify record counts
   docker-compose exec mongodb mongosh notion_bot --eval "
     print('Tasks: ' + db.tasks.countDocuments({}));
     print('Users: ' + db.users.countDocuments({}));
     print('Workspaces: ' + db.workspaces.countDocuments({}));
   "
   ```

### Backup Best Practices

1. **Retention Policy**:
   - Daily backups: Keep 7 days
   - Weekly backups: Keep 4 weeks
   - Monthly backups: Keep 12 months

2. **Test Restores**:
   - Test restore procedure monthly
   - Verify data integrity after restore
   - Document restore time

3. **Off-site Storage**:
   - Store backups in cloud storage
   - Use different region/availability zone
   - Encrypt backups at rest

4. **Monitoring**:
   - Alert on backup failures
   - Monitor backup size trends
   - Verify backup completion

---

## Handling Notion API Rate Limits

### Understanding Rate Limits

Notion API limits:
- **~3 requests per second** per integration
- Short bursts of up to 10 requests tolerated
- Rate limits are per integration token

### Monitoring Rate Limits

```bash
# Check rate limit hits
curl http://localhost:8000/metrics | grep rate_limit_hits_total

# View rate limit errors in logs
docker-compose logs api | grep -i "rate limit"

# Monitor Notion API call rate
watch -n 5 'curl -s http://localhost:8000/metrics | grep notion_api_calls_total'
```

### When Rate Limits Are Hit

The API automatically handles rate limits with:

1. **Exponential Backoff**:
   - Initial delay: 1 second
   - Doubles each retry (1s → 2s → 4s → 8s)
   - Maximum delay: 8 seconds

2. **Jitter**: ±20% randomization to prevent thundering herd

3. **Retries**: Up to 4 retries (5 total attempts)

### Reducing Rate Limit Hits

**1. Implement Caching**:

```python
# Cache frequently accessed data
from cachetools import TTLCache

cache = TTLCache(maxsize=1000, ttl=300)  # 5-minute cache

@cached(cache)
async def get_task_from_notion(page_id):
    return await notion_client.pages.retrieve(page_id)
```

**2. Batch Operations**:

Instead of:
```python
for task_id in task_ids:
    await sync_task(task_id)  # Multiple API calls
```

Use:
```python
# Batch sync with delays
for i, task_id in enumerate(task_ids):
    await sync_task(task_id)
    if i % 3 == 0:  # Every 3 requests
        await asyncio.sleep(1)  # Wait 1 second
```

**3. Prioritize Critical Operations**:

- Defer non-urgent syncs
- Use task queue for background syncs
- Implement sync scheduling

**4. Monitor and Alert**:

Set up alerts for rate limit hits:

```yaml
- alert: HighRateLimitHits
  expr: increase(rate_limit_hits_total[1h]) > 50
  annotations:
    summary: "Excessive Notion API rate limit hits"
    description: "Consider implementing caching or reducing call frequency"
```

### Emergency Rate Limit Response

If rate limits are consistently hit:

1. **Immediate actions**:
   ```bash
   # Check current call rate
   docker-compose logs api | grep "Notion API" | tail -100
   
   # Identify high-volume endpoints
   curl http://localhost:8000/metrics | grep notion_api_calls
   ```

2. **Temporary mitigations**:
   - Enable aggressive caching
   - Disable non-critical sync operations
   - Throttle incoming requests

3. **Long-term solutions**:
   - Implement Redis cache for Notion data
   - Use webhooks instead of polling
   - Request rate limit increase from Notion (enterprise plans)
   - Consider multiple integrations with separate rate limits

---

## Performance Tuning

### Database Optimization

**1. Add Indexes**:

```javascript
// Connect to MongoDB
docker-compose exec mongodb mongosh notion_bot

// Create indexes
db.tasks.createIndex({ "user_id": 1 })
db.tasks.createIndex({ "status": 1, "created_at": -1 })
db.tasks.createIndex({ "notion_page_id": 1 })
db.tasks.createIndex({ "updated_at": -1 })

// Check index usage
db.tasks.explain().find({ user_id: "user123" })
```

**2. Connection Pooling**:

Ensure optimal pool size in MongoDB URI:

```env
MONGODB_URI=mongodb://mongodb:27017/notion_bot?maxPoolSize=50&minPoolSize=10
```

**3. Query Optimization**:

```python
# Bad: Fetches all fields
tasks = await db.tasks.find({}).to_list(length=100)

# Good: Project only needed fields
tasks = await db.tasks.find(
    {},
    {"title": 1, "status": 1, "created_at": 1}
).to_list(length=100)
```

### Application Optimization

**1. Async Operations**:

Ensure all I/O operations are async:

```python
# Use asyncio.gather for parallel operations
results = await asyncio.gather(
    get_task(task_id),
    get_user(user_id),
    get_workspace(workspace_id)
)
```

**2. Response Compression**:

Enable gzip compression in production:

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**3. Connection Keep-Alive**:

```python
# Configure HTTP client with connection pooling
from httpx import AsyncClient, Limits

client = AsyncClient(
    limits=Limits(max_keepalive_connections=20, max_connections=100)
)
```

### Infrastructure Scaling

**Vertical Scaling** (increase resources):

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

**Horizontal Scaling** (multiple instances):

```yaml
services:
  api:
    deploy:
      replicas: 3
      
  # Add load balancer
  nginx:
    # ... nginx config for load balancing
```

---

## Incident Response

### Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| **P0 - Critical** | Complete service outage | < 15 minutes | API down, database crashed |
| **P1 - High** | Major functionality impaired | < 1 hour | High error rate, severe performance degradation |
| **P2 - Medium** | Partial functionality affected | < 4 hours | Single endpoint failing, minor performance issues |
| **P3 - Low** | Minor issues | < 24 hours | UI glitches, low-priority bugs |

### Incident Response Checklist

**1. Detect** (via monitoring alerts or user reports)

**2. Assess**:
- [ ] Identify affected components
- [ ] Determine severity level
- [ ] Estimate user impact

**3. Respond**:
- [ ] Notify stakeholders
- [ ] Create incident ticket
- [ ] Assign incident lead
- [ ] Begin investigation

**4. Mitigate**:
- [ ] Implement temporary fix if available
- [ ] Rollback recent changes if applicable
- [ ] Scale resources if needed

**5. Resolve**:
- [ ] Implement permanent fix
- [ ] Verify resolution
- [ ] Monitor for recurrence

**6. Document**:
- [ ] Write post-mortem
- [ ] Update runbook
- [ ] Identify prevention measures

---

## Maintenance Procedures

### Planned Downtime

1. **Schedule maintenance window** (notify users in advance)
2. **Create backup**
3. **Put maintenance page** (optional)
4. **Stop services**:
   ```bash
   docker-compose down
   ```
5. **Perform maintenance** (updates, migrations, etc.)
6. **Test in staging**
7. **Start services**:
   ```bash
   docker-compose up -d
   ```
8. **Verify health**
9. **Monitor for issues**

### Database Migrations

```bash
# Before migration: backup!
./scripts/backup.sh

# Run migration
docker-compose exec api python -m alembic upgrade head

# Verify migration
docker-compose exec mongodb mongosh notion_bot --eval "db.getCollectionNames()"

# If issues: rollback
docker-compose exec api python -m alembic downgrade -1
```

### Log Rotation

Configure logrotate (`/etc/logrotate.d/notion-bot`):

```
/var/log/notion-bot/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        docker-compose restart api > /dev/null 2>&1
    endscript
}
```

---

## Additional Resources

- [Notion API Status](https://status.notion.so/)
- [MongoDB Operations Best Practices](https://docs.mongodb.com/manual/administration/production-notes/)
- [Docker Logging Best Practices](https://docs.docker.com/config/containers/logging/)

---

## Emergency Contacts

- **On-Call Engineer**: [pager/phone]
- **DevOps Team**: [email/slack]
- **Database Admin**: [contact]
- **Notion Support**: https://www.notion.so/help/contact-support
