from pydantic import field_validator

class Settings(BaseSettings): # type: ignore
    model_config = SettingsConfigDict( # type: ignore
        env_file=".env",
        extra="ignore"
    )

    # ...

    @classmethod
    def settings_customise_sources(
        cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings
    ):
        import os

        # Cuando pytest está corriendo, ignoramos por completo .env real
        if os.getenv("PYTEST_CURRENT_TEST"):
            return (init_settings, env_settings)  # NO dotenv_settings

        # Flujo normal para prod/dev
        return (init_settings, env_settings, dotenv_settings, file_secret_settings)
