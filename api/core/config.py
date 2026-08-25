"""
Application settings
Manage environment variables and default settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # SQLite-only local research-prototype persistence. Not PostgreSQL.
    # Override with DB_URL (e.g. sqlite:////tmp/test.db) for tests.
    db_url: str = "sqlite:///data/medigator.db"

    # API settings
    api_title: str = "Medigator Research Prototype API"
    api_version: str = "1.0.0"
    debug: bool = False

    # CORS settings
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    # Optional: CORS origins from environment (comma-separated)
    cors_origins_csv: str | None = None

    # OpenAI settings
    OPENAI_API_KEY: str | None = None
    LLM_MODEL: str = "gpt-4o-mini"  # Match client default
    LLM_TEMPERATURE: float = 0.1  # Low temperature for stability
    LLM_TOP_P: float = 0.9  # Controlled randomness
    LLM_TIMEOUT_MS: int = 3500
    LLM_SEED: int = 42  # Fixed seed for reproducibility

    # Demo settings
    # DEMO_MODE does not make arbitrary identifiers safe. See SYNTHETIC_DATA_ONLY.
    DEMO_MODE: bool = True
    SYNTHETIC_DATA_ONLY: bool = True
    # Leftover flag from earlier prototypes; not a compliance certification.
    HIPAA_MODE: bool = False
    # Shared demo operator password for portfolio use only — not production IAM.
    DEMO_ACCESS_CODE: str = "replace-me-locally"

    # PDF settings
    PDF_OUTPUT_DIR: str = "./reports"

    # Data file path
    data_dir: str = "./data"
    rules_dir: str = "./data/rules"
    fhir_dir: str = "./data/fhir"

    # RAG settings
    enable_rag: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS origins from CSV if provided
        if self.cors_origins_csv:
            csv_origins = [
                origin.strip()
                for origin in self.cors_origins_csv.split(",")
                if origin.strip()
            ]
            self.cors_origins.extend(csv_origins)


# Global settings instance
settings = Settings()
