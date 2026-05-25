from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, timezone

# --- Request Schemas ---

class TransactionRequest(BaseModel):
    city_pop: float
    hour: float
    age: float
    unix_time: float
    amt_diff_avg_30d: float
    trans_count_24h: float
    distance_velocity: float
    merchant_risk_score: float
    merchant_freq_30d: float
    cat_misc_net: float
    cat_grocery_pos: float
    cat_entertainment: float
    cat_gas_transport: float
    cat_misc_pos: float
    cat_grocery_net: float
    cat_shopping_net: float
    cat_shopping_pos: float
    cat_food_dining: float
    cat_personal_care: float
    cat_health_fitness: float
    cat_travel: float
    cat_kids_pets: float
    cat_home: float
    user_id: Optional[str] = "default_user"

# --- Response Schemas ---

class ImmediateResponse(BaseModel):
    transaction_id: str
    score: float
    prediction: str
    status: str  # "completed" or "explaining"
    explanation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ExplanationResponse(BaseModel):
    explanation_id: str
    status: str # "pending", "completed", "failed"
    score: float
    top_factors: List[str]
    natural_language_explanation: Optional[str] = None
    risk_level: str
    generated_at: Optional[datetime] = None

class ModeToggleRequest(BaseModel):
    mode: Literal["rule_based", "nlp"]

# --- Internal Feature Schema (23 features total) ---

class InferenceFeatures(BaseModel):
    city_pop: float
    hour: float
    age: float
    unix_time: float
    amt_diff_avg_30d: float
    trans_count_24h: float
    distance_velocity: float
    merchant_risk_score: float
    merchant_freq_30d: float
    cat_misc_net: float
    cat_grocery_pos: float
    cat_entertainment: float
    cat_gas_transport: float
    cat_misc_pos: float
    cat_grocery_net: float
    cat_shopping_net: float
    cat_shopping_pos: float
    cat_food_dining: float
    cat_personal_care: float
    cat_health_fitness: float
    cat_travel: float
    cat_kids_pets: float
    cat_home: float

    def to_numpy_array(self):
        import numpy as np
        return np.array([[
            self.city_pop, self.hour, self.age, self.unix_time,
            self.amt_diff_avg_30d, self.trans_count_24h, self.distance_velocity,
            self.merchant_risk_score, self.merchant_freq_30d,
            self.cat_misc_net, self.cat_grocery_pos, self.cat_entertainment,
            self.cat_gas_transport, self.cat_misc_pos, self.cat_grocery_net,
            self.cat_shopping_net, self.cat_shopping_pos, self.cat_food_dining,
            self.cat_personal_care, self.cat_health_fitness, self.cat_travel,
            self.cat_kids_pets, self.cat_home
        ]], dtype=np.float32)
