import redis
import json
from app.config import settings

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )

    def store_explanation(self, explanation_id: str, data: dict):
        """Store the LLM explanation result with a TTL."""
        self.client.setex(
            f"explanation:{explanation_id}",
            settings.REDIS_EXP_TTL,
            json.dumps(data)
        )

    def get_explanation(self, explanation_id: str) -> dict:
        """Retrieve stored explanation."""
        data = self.client.get(f"explanation:{explanation_id}")
        return json.loads(data) if data else None

    def set_explanation_mode(self, mode: str):
        """Set the global explanation mode (rule_based or nlp)."""
        self.client.set("config:explanation_mode", mode)

    def get_explanation_mode(self) -> str:
        """Get the current global explanation mode. Defaults to rule_based."""
        mode = self.client.get("config:explanation_mode")
        return mode if mode else "rule_based"

redis_service = RedisClient()
