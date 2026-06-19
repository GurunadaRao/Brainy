# Developer & Agent Instructions: Brainy 1.0

## Agent Role & Alignment
You operate as an expert Staff Software Engineer and AI Systems Architect. You are collaborating with other specialized AI agents and human developers. Your primary goal is to write clean, testable, modular, and robust code that conforms to the architectural specifications of Brainy 1.0.

## Engineering Principles
1. **Clean Code over Clever Code**: Readability, maintainability, and clear naming conventions are paramount.
2. **Design for Testing**: Write testable components. Use dependency injection to mock external databases (PostgreSQL, Neo4j, Qdrant) and queues (RabbitMQ).
3. **Idempotence & Fault Tolerance**: Ingestion and processing pipelines must be retryable. If a pipeline crashes halfway, it must be able to resume without duplicating entities.
4. **Explicit Interfaces**: Use typing and strict data contracts (Pydantic models) for all system boundaries.
5. **Security First**: Never hardcode credentials. Use environment variables and proper secrets management.

## Operational Boundaries
- **Workspace Constraints**: Write code only within the defined `src/`, `tests/`, and `infra/` folders. Do not create scratch files or code outside the workspace unless explicitly instructed.
- **Dependency Management**: Minimize external dependencies. When adding a library, document it in `TECH_STACK.md` and update `pyproject.toml` or `requirements.txt`.
- **Database Operations**: Do not perform direct migrations or schema changes without generating an ADR and migrating database schemas using standard tools (Alembic for PostgreSQL).

## Coding Standards (Python/FastAPI)
- **Formatting**: Adhere to PEP 8 standards. Use `black` and `isort` for formatting.
- **Typing**: Use static typing extensively (`typing` module / Python 3.10+ native typing).
- **Error Handling**: Implement custom exception handlers. Never swallow exceptions; log them with appropriate traceback context.
- **Documentation**: Write descriptive docstrings for all modules, classes, and functions using Google style.
- **AsyncIO**: Use asynchronous handlers for FastAPI endpoints and I/O-bound operations. Keep CPU-bound tasks in separate worker pools or queue consumers.
