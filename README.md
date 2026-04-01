# Task Approval Workflow API

Simple FastAPI service that demonstrates:
- polymorphic task models (Pydantic discriminated unions),
- layered architecture (router -> controller -> repository),
- approval workflow state transitions.

## Project structure

- `main.py` - app setup
- `models/tasks.py` - task types and request models
- `routers/tasks.py` - HTTP endpoints only
- `controllers/task_controller.py` - business rules and transitions
- `repositories/task_repo.py` - async in-memory repository
- `tests/test_tasks.py` - API tests with FastAPI TestClient

## Architecture decisions

- **Router layer** only handles HTTP and delegates to controller.
- **Controller layer** contains business logic (state transitions and guards).
- **Repository layer** abstracts storage behind async methods.

This keeps responsibilities clear and makes each layer easier to test in isolation.

## Polymorphism approach

`AnyTask` is a discriminated union using the `type` field:
- `data_access`
- `resource_provision`
- `config_change`

Each subtype contains its own validation rules via model validators.

## Endpoints

- `POST /tasks/`
- `GET /tasks/{id}`
- `PATCH /tasks/{id}/approve`
- `PATCH /tasks/{id}/reject`

Valid transitions:
- `PENDING -> APPROVED`
- `PENDING -> REJECTED`

Any second action on an already resolved task returns `409 Conflict`.

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Run tests

```bash
pytest -q
```

## What to change for production

- Replace in-memory store with database persistence (e.g., PostgreSQL + SQLAlchemy).
- Add authentication/authorization at router boundary.
- Add logging, metrics, and tracing.
- Add caching for read-heavy flows.
- Add migrations and stronger error handling conventions.
