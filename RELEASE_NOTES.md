# Release Notes

## [Unreleased]

### Added
- Initial Alembic migration for RBAC: creates `users`, `roles`, `permissions`, `user_roles`, `role_permissions` with FKs and indexes.
- Unified RBAC models/services/routers; consistent JWT handling returning TokenData.
- Expanded RBAC test suite (auth, users CRUD, roles/permissions, me, refresh) — 15 tests passing.
- `.env.example` covering API, JWT, DB, App, Server, CORS.
- Documentation updates: README RBAC section; comprehensive `docs/RBAC_GUIDE.md`.
- CI workflow (GitHub Actions) running `alembic upgrade head` + `pytest` on PRs.

### Changed
- Seeded default roles: `admin` (all permissions), `auditor` (read-only), `customer` (no users access).
- Operator endpoints accept API Key or JWT (flex auth).

### Migration
- Apply: `alembic upgrade head`.
- Dev reset (optional): remove `app.db`/`test.db`, then `alembic upgrade head`.

### How to test
- `pytest -q` → expected: all tests passing.

### Notes
- Existing deployments must apply migrations before starting the app.

---

## Resumen esencial (ES)
- Migraciones Alembic iniciales para RBAC, modelos/servicios/routers unificados, tests ampliados (15 OK), `.env.example`, documentación RBAC, y CI con migraciones + tests. Ejecuta `alembic upgrade head` y `pytest -q`.
