from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str
    redis_url: str = "redis://localhost:6379"
    business_name: str = "R&M Plumbing and Heating"
    google_review_url: str = ""
    google_cloud_project: str = ""
    session_ttl: int = 86400  # 24 hours
    rate_limit_window: int = 60
    rate_limit_max: int = 30

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
