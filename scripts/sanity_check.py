#!/usr/bin/env python3
"""Sanity check script to validate the project structure and imports."""

import sys
import os

def check_project_structure():
    """Check that all required files and directories exist."""
    
    required_files = [
        "src/main.py",
        "src/config/settings.py",
        "src/core/database/connection.py",
        "src/core/notion/client.py",
        "src/core/notion/rate_limiter.py",
        "src/core/errors/exceptions.py",
        "src/core/errors/error_handler.py",
        "src/features/tasks/routes.py",
        "src/features/tasks/dto/create_task_request.py",
        "src/features/tasks/dto/create_task_response.py",
        "src/features/tasks/services/notion_task_service.py",
        "src/features/workspaces/routes.py",
        "src/features/workspaces/dto/create_workspace_request.py",
        "src/features/workspaces/dto/workspace_response.py",
        "src/features/workspaces/services/workspace_service.py",
        "src/features/workspaces/repository.py",
        "src/features/workspaces/models.py",
        "pyproject.toml",
        "docker-compose.yml",
        ".env.example"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("✅ All required files present")
        return True


def check_imports():
    """Check that core imports work."""
    
    try:
        # Add src to path for imports
        sys.path.insert(0, 'src')
        
        # Test basic imports
        print("🔍 Testing imports...")
        
        from config.settings import get_settings
        print("✅ Config imports work")
        
        import core.database.connection
        print("✅ Database imports work")
        
        import core.notion.client
        print("✅ Notion client imports work")
        
        import core.notion.rate_limiter
        print("✅ Rate limiter imports work")
        
        import core.errors.exceptions
        print("✅ Error imports work")
        
        import tasks.dto.create_task_request
        print("✅ Task DTO imports work")
        
        import workspaces.models
        print("✅ Workspace models imports work")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def check_config():
    """Check configuration defaults work."""
    
    try:
        sys.path.insert(0, 'src')
        
        # Test settings with empty environment (should use defaults)
        os.environ.clear()
        os.environ.setdefault('NOTION_API_KEY', 'test_key')
        
        from config.settings import get_settings
        settings = get_settings()
        
        # Verify defaults
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.log_level == "INFO"
        assert settings.notion_api_version == "2022-10-28"
        
        print("✅ Configuration defaults work")
        return True
        
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        return False


def main():
    """Run all sanity checks."""
    
    print("🔍 Running Sanity Checks")
    print("=" * 40)
    
    checks = [
        ("Project Structure", check_project_structure),
        ("Import Dependencies", check_imports), 
        ("Configuration", check_config)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        result = check_func()
        if not result:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All checks passed! Project is ready for development.")
    else:
        print("⚠️  Some checks failed. Please fix issues before development.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
