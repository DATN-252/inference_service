from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Minimalist ML Inference Service"
    DEBUG: bool = False
    
    # ML Config
    RISK_THRESHOLD: float = 0.5
    MODEL_PATH: str = "models/packaged_model_round_100.onnx"
    
    # Redis Config
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_EXP_TTL: int = 3600  # 1 hour TTL for explanations
    
    # Celery Config
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    class Config:
        env_file = ".env"

settings = Settings()
