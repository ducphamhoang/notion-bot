# Deployment Checklist

Use this checklist to ensure successful deployment of the Notion Bot API.

## Pre-Deployment

- [ ] Verify system meets [prerequisites](DEPLOYMENT.md#prerequisites)
  - [ ] Docker 20.10+ installed
  - [ ] Docker Compose 2.0+ installed
  - [ ] Git installed
- [ ] Clone the repository
  - [ ] `git clone <repository-url>`
  - [ ] `cd notion-bot`
- [ ] Configure environment variables
  - [ ] `cp .env.example .env`
  - [ ] Update `NOTION_API_KEY` with valid token
  - [ ] Update other variables as needed (database URI, CORS, etc.)
- [ ] For production deployments:
  - [ ] Create `.env.prod` with production settings
  - [ ] Verify MongoDB connection settings
  - [ ] Set appropriate log levels (e.g., WARNING instead of INFO)

## During Deployment

- [ ] Run the deployment script: `./deploy.sh` or `.\deploy.ps1`
  - [ ] Use `-e prod` flag for production deployments
- [ ] Monitor the deployment process
  - [ ] Watch for any error messages
  - [ ] Verify all services start successfully
- [ ] Wait for health checks to pass
  - [ ] Verify the health endpoint returns "healthy"
  - [ ] Confirm all services are "Up" in `docker-compose ps`

## Post-Deployment Verification

- [ ] Check the health endpoint: `curl http://localhost:8000/health`
  - [ ] Should return JSON with `"status": "healthy"`
- [ ] Verify the API root: `curl http://localhost:8000/`
  - [ ] Should return API information
- [ ] Access the API documentation: `http://localhost:8000/docs`
  - [ ] Should load the Swagger UI
- [ ] Check service status: `docker-compose ps`
  - [ ] All services should show "Up"
- [ ] Review application logs: `docker-compose logs app`
  - [ ] Should not contain critical errors
  - [ ] Should show successful startup messages

## Security Checks

- [ ] Verify `DEBUG` is set to `false` in production
- [ ] Confirm CORS settings are restrictive (not wildcard *)
- [ ] Check that sensitive environment variables are not exposed in logs
- [ ] Verify that the API is only accessible from allowed domains

## Performance Verification

- [ ] Test API response times under normal load
- [ ] Monitor resource usage (CPU, memory) of containers
- [ ] Verify database connection pooling is working correctly

## Rollback Plan

- [ ] Document how to stop the deployment: `./deploy.sh --stop`
- [ ] Have backup of previous environment files if needed
- [ ] Verify you can redeploy if issues are found

## Common Issues to Check

- [ ] Database connection issues (check MongoDB logs)
- [ ] Notion API key permissions (verify integration has DB access)
- [ ] Port conflicts (ensure 8000 and 27017 are available)
- [ ] Environment variable misconfigurations
- [ ] Docker resource limits (memory, CPU)

## Post-Deployment Tasks

- [ ] Update your team/organization about the deployment
- [ ] Document any custom configurations used
- [ ] Set up monitoring and alerts if needed
- [ ] Schedule regular backup procedures
- [ ] Plan for periodic security reviews