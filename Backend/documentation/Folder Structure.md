# Backend Folder Structure Documentation

## Top-Level Files

- **main.py** – Application entry point; starts FastAPI app, registers routes, and initializes database and middleware.
- **config.py** – Central place for environment variables and app configuration (DB URL, secrets, feature flags).
- **README.md** – Project overview, instructions, and notes.
- **requirements.txt / pyproject.toml** – Lists project dependencies.
- **Dockerfile** – Defines how to containerize the app.
- **.env** – Environment variables (like DB URL, JWT secrets).

## Folders

### models/
- Contains ORM models that represent database tables.
- Example files: `user_models.py`, `auth_models.py`, `conversation_models.py`.
- Purpose: Define database structure, relationships, and constraints.

### schemas/
- Contains Pydantic schemas for validation and shaping API input/output.
- Example files: `user_schema.py`, `auth_schema.py`.
- Purpose: Ensure consistent input from clients and structured output in responses.

### crud/
- Contains functions to interact with the database (Create, Read, Update, Delete).
- Example files: `user_crud.py`, `conversation_crud.py`.
- Purpose: Keep all database operations separate from business logic.

### api/
- Contains HTTP routes exposed to clients.
- Example files: `user_routes.py`, `auth_routes.py`.
- Purpose: Connect external requests to the services layer.

### services/
- Contains business logic and internal operations.
- Example files: `user_service.py`, `conversation_service.py`.
- Purpose: Coordinate multiple CRUD calls, validate logic, and provide a clean interface for routes or other services.
- **Note**: Internal services use Python calls instead of HTTP in monolith; ready for microservices later.

### database/
- Contains DB engine, session management, and base model.
- Example files: `connection.py`, `base.py`.
- Purpose: Centralized database setup and session handling for all services.

### core/
- Contains shared utilities, security functions, and helpers.
- Example files: `security.py`, `utils.py`.
- Purpose: Reusable functions and modules across all services (e.g., password hashing, token handling, logging).

### tests/
- Unit and integration tests.
- Mirrors app structure to test models, services, and API routes.

### scripts/
- Automation scripts (DB seeding, cron jobs, migrations).

### alembic/
- Database migration files for versioning schema changes.

## High-Level Notes

### Monolithic simplicity
- All services share a single database and can call each other directly using Python functions.

### Microservice-ready
- Each domain (user, auth, conversation) has separate models, CRUD, schemas, services, and routes. Later, these can be extracted into separate microservices with minimal refactoring.

### Clear separation of concerns
- **Models** → database tables
- **Schemas** → validation and API contract
- **CRUD** → raw database operations
- **Services** → business logic
- **API** → HTTP layer for external clients

### Internal calls vs API calls
- Internal logic uses Python objects; API routes are primarily for external requests.

This structure keeps the monolith organized, testable, and scalable while laying the groundwork for a future microservices architecture.
