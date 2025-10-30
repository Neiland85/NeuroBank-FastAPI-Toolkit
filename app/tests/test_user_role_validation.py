# I have the following comments after thorough review of file. Implement the comments by following the instructions verbatim.
#
# ---
# ## Comment 1: `get_current_user` no carga relaciones; `require_permissions` provoca N+1 queries y potenciales problems de sesión.
#
# En `app/auth/dependencies.py` modifique la consulta de `get_current_user` para incluir `selectinload(User.roles).selectinload(Role.permissions)`. Importe `Role` para el eager load. Alternativamente, reutilice `get_user_by_username()` del `user_service` y pase la sesión. Verifique con tests de autorización que no se realizan consultas adicionales.
#
# ### Relevant Files
# - /Users/estudio/Projects/GitHub/PYTHON3/NeuroBank-FastAPI-Toolkit/NeuroBank-FastAPI-Toolkit-1/app/auth/dependencies.py
# - /Users/estudio/Projects/GitHub/PYTHON3/NeuroBank-FastAPI-Toolkit/NeuroBank-FastAPI-Toolkit-1/app/services/user_service.py
# --- I have the following comments after thorough review of file. Implement the comments by following the instructions verbatim.
#
# ---
# ## Comment 1: `role_service` lanza `ValueError` que deriva en 500; los routers no mapean a 4xx.
#
# En `app/services/errors.py` defina excepciones de dominio (`RoleNotFoundError`, `SystemRoleDeletionError`). En `app/services/role_service.py` reemplace `ValueError` por esas excepciones. En `app/main.py` agregue `@app.exception_handler` para mapear a 404 (no encontrado) y 400 (reglas de negocio). Alternativamente, capture en `app/routers/roles.py` y lance `HTTPException` con el código correcto.
#
# ### Relevant Files
# - /Users/estudio/Projects/GitHub/PYTHON3/NeuroBank-FastAPI-Toolkit/NeuroBank-FastAPI-Toolkit-1/app/services/role_service.py
# - /Users/estudio/Projects/GitHub/PYTHON3/NeuroBank-FastAPI-Toolkit/NeuroBank-FastAPI-Toolkit-1/app/services/errors.py
# - /Users/estudio/Projects/GitHub/PYTHON3/NeuroBank-FastAPI-Toolkit-1/app/main.py
# - /Users/estudio/Projects/GitHub/PYTHON3/NeuroBank-FastAPI-Toolkit-1/app/routers/roles.py
# --- I have the following comments after thorough review of file. Implement the comments by following the instructions verbatim.
#
# ---
# ## Comment 1: `Settings` referencia `self.secret_key` sin definirlo, causando fallo en producción y debilitando la validación de JWT.
#
# En `app/config.py` la clase `Settings` usa `self.secret_key` en la validación pero no define el atributo. Defina `secret_key: str | None = os.getenv('SECRET_KEY')` si pretende soportarlo o elimine su uso del conditional. Ajuste la validación para exigir `jwt_secret_key` en producción. Actualice `.env.example` y el README con `JWT_SECRET_KEY`. Verifique que `get_settings()` y pruebas integradas contemplen el nuevo atributo o el cambio de validación.
#
# ### Relevant Files
# - /Users/estudio/Projects/GitHub/PYTHON3/NeuroBank-FastAPI-Toolkit-1/app/config.py
import pytest

from app.database import AsyncSessionLocal
from app.schemas import UserCreate
from app.services.errors import ValidationError
from app.services.user_service import create_user


@pytest.mark.anyio
async def test_create_user_with_nonexistent_role_raises_validation_error():
    async with AsyncSessionLocal() as db:
        payload = UserCreate(
            username="nouserrole",
            email="nouserrole@example.com",
            password="StrongPass123!",  # noqa: S106 (valor de prueba)
            full_name=None,
        )
        with pytest.raises(ValidationError) as excinfo:
            await create_user(db, payload, roles=["rol_que_no_existe"])
        # Mensaje debe coincidir con el formato de assign_roles
        assert "Roles inexistentes:" in str(excinfo.value)
        assert "rol_que_no_existe" in str(excinfo.value)
