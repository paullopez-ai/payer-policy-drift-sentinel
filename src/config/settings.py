from __future__ import annotations

import os


def _bool_env(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default)).lower() in ("true", "1", "yes")


class Settings:
    app_env: str = os.getenv("APP_ENV", "local")
    mock_llm: bool = _bool_env("MOCK_LLM", True)
    external_client_mode: str = os.getenv("EXTERNAL_CLIENT_MODE", "mock")

    max_prompt_tokens: int = int(os.getenv("MAX_PROMPT_TOKENS", "12000"))
    max_completion_tokens: int = int(os.getenv("MAX_COMPLETION_TOKENS", "1800"))
    max_run_cost_usd: float = float(os.getenv("MAX_RUN_COST_USD", "5.00"))
    max_databricks_job_wait_seconds: int = int(
        os.getenv("MAX_DATABRICKS_JOB_WAIT_SECONDS", "900")
    )
    snowflake_query_timeout_seconds: int = int(
        os.getenv("SNOWFLAKE_QUERY_TIMEOUT_SECONDS", "60")
    )

    snowflake_account: str = os.getenv("SNOWFLAKE_ACCOUNT", "")
    snowflake_user: str = os.getenv("SNOWFLAKE_USER", "")
    snowflake_role: str = os.getenv("SNOWFLAKE_ROLE", "PAYER_DRIFT_APP_ROLE")
    snowflake_warehouse: str = os.getenv("SNOWFLAKE_WAREHOUSE", "PAYER_DRIFT_WH")
    snowflake_database: str = os.getenv("SNOWFLAKE_DATABASE", "PAYER_DRIFT_SENTINEL")
    snowflake_private_key_path: str = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH", "")

    databricks_host: str = os.getenv("DATABRICKS_HOST", "")
    databricks_token: str = os.getenv("DATABRICKS_TOKEN", "")
    databricks_warehouse_id: str = os.getenv("DATABRICKS_WAREHOUSE_ID", "")
    databricks_drift_job_id: str = os.getenv("DATABRICKS_DRIFT_JOB_ID", "")

    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")

    @property
    def is_mock(self) -> bool:
        return self.mock_llm or self.external_client_mode == "mock"

    @property
    def is_live(self) -> bool:
        return not self.mock_llm and self.external_client_mode == "live"


settings = Settings()
