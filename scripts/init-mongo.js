// MongoDB initialization script for notion-bot database

// Switch to notion-bot database
db = db.getSiblingDB('notion-bot');

// Create collections with initial structure
db.createCollection('workspaces');
db.createCollection('users');

// Create indexes for workspaces collection
db.workspaces.createIndex(
  { platform: 1, platform_id: 1 },
  { unique: true, name: 'idx_platform_platform_id_unique' }
);

// Create indexes for users collection
db.users.createIndex(
  { platform: 1, platform_user_id: 1 },
  { unique: true, name: 'idx_platform_platform_user_id_unique' }
);

// Add some sample data (optional)
// Sample workspace
db.workspaces.insertOne({
  platform: 'web',
  platform_id: 'default_workspace',
  notion_database_id: 'your_database_id_here',
  name: 'Default Workspace',
  created_at: new Date(),
  updated_at: new Date()
});

print('MongoDB initialization completed successfully!');
