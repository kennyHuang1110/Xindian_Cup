# Migrations

Alembic is configured for schema migration management.

Common commands:

```bash
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "describe change"
```
