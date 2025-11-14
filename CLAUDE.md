<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->
# Notion Bot - Dependency Injection Pattern

## CRITICAL: All Services MUST Follow This Pattern

When creating or modifying services, **ALWAYS** use Dependency Injection:

```python
from typing import Optional

class MyService:
    def __init__(self, repository: Optional[MyRepository] = None):
        """
        Service with optional repository injection for testability.
        
        Args:
            repository: Optional repository for testing.
                       Defaults to production repository if not provided.
        """
        self._repository = repository or MyRepository()
```

## Why This Pattern?

1. **Testable**: Easy to inject mock repositories in tests
2. **Clean**: No monkey-patching or hacky mocks needed
3. **FastAPI Native**: Uses dependency override system
4. **Backward Compatible**: Existing code works unchanged
5. **SOLID**: Follows dependency inversion principle

## Testing with DI

In `tests/conftest.py`, use FastAPI's dependency override:

```python
from fastapi import FastAPI

@pytest.fixture
def mock_workspace_service():
    """Override workspace service with mock."""
    mock_repo = Mock(spec=WorkspaceRepository)
    
    def override_service():
        return WorkspaceService(repository=mock_repo)
    
    app.dependency_overrides[get_workspace_service] = override_service
    yield mock_repo
    app.dependency_overrides.clear()
```

## Error Handling

Domain exceptions bubble up to global handler:

```python
# In services - just raise domain exceptions
if not result:
    raise NotFoundError(
        entity_type="Workspace",
        entity_id=workspace_id
    )

# In main.py - handler converts to HTTP responses
@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return handle_domain_exception(exc)
```

**DO NOT wrap service calls in try-except to convert to HTTPException!**

## References

- Full architecture: `@docs/agents/dev.md`
- DI implementation: `DI_IMPLEMENTATION_SUCCESS.md`
- Test examples: `tests/conftest.py`
