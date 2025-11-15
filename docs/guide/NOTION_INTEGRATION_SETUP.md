# Notion Integration Setup Guide

This guide walks you through setting up a Notion integration and obtaining the API credentials needed for the Notion Bot API.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1: Create a Notion Integration](#step-1-create-a-notion-integration)
- [Step 2: Get Your API Key](#step-2-get-your-api-key)
- [Step 3: Share Databases with Your Integration](#step-3-share-databases-with-your-integration)
- [Step 4: Configure the Notion Bot API](#step-4-configure-the-notion-bot-api)
- [Step 5: Verify the Connection](#step-5-verify-the-connection)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

1. **A Notion account** - Sign up at [notion.so](https://www.notion.so) if you don't have one
2. **Notion workspace admin access** - Required to create integrations
3. **At least one Notion database** - This will store your tasks

---

## Step 1: Create a Notion Integration

1. **Navigate to Notion Integrations**
   - Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
   - Or: Click on **Settings & Members** → **Connections** → **Develop or manage integrations**

2. **Create New Integration**
   - Click **"+ New integration"**
   - You'll see a form with the following fields

3. **Configure Integration Settings**

   **Basic Information**:
   - **Name**: `Notion Bot API` (or your preferred name)
   - **Associated workspace**: Select your workspace from the dropdown
   - **Logo**: (Optional) Upload a logo for your integration

   **Capabilities** (check the following):
   - ✅ **Read content**
   - ✅ **Update content** 
   - ✅ **Insert content**
   - ✅ **Read user information including email addresses** (if you need user mapping)
   - ✅ **Read comments**
   - ✅ **Insert comments** (optional, for task comments)

   **Integration Type**:
   - Select **"Internal integration"** (for private use within your workspace)
   - Select **"Public integration"** only if you plan to distribute this

4. **Submit the Integration**
   - Click **"Submit"** to create the integration
   - You'll be redirected to the integration's settings page

---

## Step 2: Get Your API Key

1. After creating the integration, you'll see a **"Secrets"** section
2. Find the **"Internal Integration Token"** (also called "Internal Integration Secret")
3. Click **"Show"** and then **"Copy"** to copy the token
4. The token will look like: `secret_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

**⚠️ Important**: 
- Keep this token **secure and private**
- Never commit it to version control
- Never share it publicly
- Treat it like a password

---

## Step 3: Share Databases with Your Integration

Your integration needs explicit permission to access Notion databases.

### For Each Database You Want to Use:

1. **Open the database** in Notion
2. Click the **"•••"** (three dots) menu in the top-right corner
3. Select **"Connections"** or **"Add connections"**
4. Find and select your integration name (e.g., "Notion Bot API")
5. Click **"Confirm"** to grant access

### Get Database IDs

You'll need the database ID for configuration:

1. Open the database in Notion
2. Copy the URL from your browser
3. The URL looks like: `https://www.notion.so/workspace/DATABASE_ID?v=VIEW_ID`
4. Extract the `DATABASE_ID` part (it's a 32-character hexadecimal string)
   - Example: `12345678901234567890123456789012`

---

## Step 4: Configure the Notion Bot API

### Using Environment Variables (Recommended)

1. Create a `.env` file in the project root (if it doesn't exist):

```bash
touch .env
```

2. Add your Notion credentials:

```env
# Notion API Configuration
NOTION_API_KEY=secret_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
NOTION_DATABASE_ID=12345678901234567890123456789012

# Optional: Additional configuration
NOTION_API_TIMEOUT=30
```

3. Ensure `.env` is in your `.gitignore`:

```bash
echo ".env" >> .gitignore
```

### Using Docker Environment Variables

If deploying with Docker, add to your `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      - NOTION_API_KEY=${NOTION_API_KEY}
      - NOTION_DATABASE_ID=${NOTION_DATABASE_ID}
```

Or use Docker secrets for production:

```yaml
services:
  api:
    secrets:
      - notion_api_key
    environment:
      - NOTION_API_KEY_FILE=/run/secrets/notion_api_key

secrets:
  notion_api_key:
    external: true
```

### Configuration Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NOTION_API_KEY` | Yes | Your integration's internal token | `secret_abc123...` |
| `NOTION_DATABASE_ID` | Yes | ID of your tasks database | `12345678...` |
| `NOTION_API_TIMEOUT` | No | API request timeout in seconds | `30` (default) |

---

## Step 5: Verify the Connection

### Test the Connection

1. **Start the API**:

```bash
# Using Poetry
poetry run python -m src.main

# Using Docker
docker-compose up
```

2. **Check the health endpoint**:

```bash
curl http://localhost:8000/health
```

3. **Expected response** (success):

```json
{
  "status": "healthy",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection is healthy"
    },
    "notion": {
      "status": "healthy",
      "notion_api": {
        "status": "connected",
        "api_version": "connected"
      }
    }
  }
}
```

4. **If the response shows unhealthy**, check:
   - API key is correct and copied fully
   - Database is shared with the integration
   - Network connectivity to Notion API
   - Check application logs for detailed errors

### Test Task Creation

Create a test task to verify full functionality:

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing Notion integration",
    "status": "todo"
  }'
```

Check if the task appears in your Notion database.

---

## Troubleshooting

### Error: "unauthorized" or "Invalid API key"

**Cause**: The API key is incorrect or not configured properly.

**Solutions**:
1. Verify the API key is copied completely (starts with `secret_`)
2. Check for extra spaces or newlines in the `.env` file
3. Ensure environment variables are loaded (restart the application)
4. Regenerate the API key if necessary (Notion Integration Settings → Secrets)

### Error: "object_not_found" or "Database not found"

**Cause**: The integration doesn't have access to the database.

**Solutions**:
1. Share the database with your integration (see Step 3)
2. Verify the database ID is correct
3. Ensure the database exists and hasn't been deleted
4. Check that you're using the workspace where the integration was created

### Error: "Failed to connect to Notion API"

**Cause**: Network connectivity issues or Notion API is down.

**Solutions**:
1. Check your internet connection
2. Verify you can access https://api.notion.com
3. Check Notion status at https://status.notion.so
4. Check firewall/proxy settings
5. Verify Docker networking if using containers

### Error: "Rate limit exceeded"

**Cause**: Too many requests to Notion API.

**Solutions**:
1. The API automatically retries with backoff
2. Reduce request frequency
3. Implement caching in your client
4. Check metrics at `/metrics` to monitor rate limit hits

### Integration Not Appearing in Database Connections

**Cause**: Integration visibility or workspace permissions.

**Solutions**:
1. Ensure you're a workspace admin
2. Refresh the Notion page
3. Try searching for the integration by name
4. Recreate the integration if necessary

### Changes Not Syncing to Notion

**Cause**: Sync configuration or API issues.

**Solutions**:
1. Check application logs for sync errors
2. Verify the task has a valid `notion_page_id`
3. Manually trigger sync: `POST /tasks/{task_id}/sync`
4. Check Notion API status
5. Verify database schema matches expected fields

---

## Security Best Practices

### Protecting Your API Key

1. **Never commit** `.env` files to version control
2. **Use environment variables** or secrets management
3. **Rotate keys regularly** (at least quarterly)
4. **Use separate integrations** for development and production
5. **Limit integration capabilities** to only what's needed
6. **Monitor access logs** in Notion workspace settings

### Production Deployment

For production environments:

1. **Use secrets management**:
   - AWS Secrets Manager
   - HashiCorp Vault
   - Docker Secrets
   - Kubernetes Secrets

2. **Restrict network access**:
   - Use VPC/private networks
   - Implement firewall rules
   - Use API gateway with authentication

3. **Monitor and audit**:
   - Enable logging for all Notion API calls
   - Set up alerts for unusual activity
   - Review integration access regularly

---

## Next Steps

After successfully setting up your Notion integration:

1. **Configure MongoDB** - See [Deployment Guide](./DEPLOYMENT_GUIDE.md)
2. **Deploy the API** - Follow deployment instructions
3. **Set up monitoring** - Configure metrics and alerts
4. **Test thoroughly** - Run integration tests
5. **Review security** - Follow security best practices

---

## Additional Resources

- [Notion API Official Documentation](https://developers.notion.com/)
- [Notion API Reference](https://developers.notion.com/reference)
- [Notion API Changelog](https://developers.notion.com/page/changelog)
- [Notion Developer Community](https://developers.notion.com/community)
- [Notion Status Page](https://status.notion.so/)

---

## Support

If you encounter issues not covered in this guide:

1. Check the [Operations Runbook](./OPERATIONS_RUNBOOK.md)
2. Review application logs for detailed error messages
3. Test the integration at [Notion API Explorer](https://developers.notion.com/reference/intro)
4. Contact your development team or system administrator
