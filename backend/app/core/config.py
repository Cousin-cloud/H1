from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Capacity Planner API"
    supabase_url: str
    supabase_service_role_key: str
    supabase_jwt_secret: str
    cors_origins: str = "http://localhost:5173"


settings = Settings()
