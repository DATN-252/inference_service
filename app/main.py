import uuid
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from app.config import settings
from app.schemas import (
    TransactionRequest, ImmediateResponse, ExplanationResponse, 
    InferenceFeatures, ModeToggleRequest
)
from app.services.dl_engine import dl_engine
from app.services.redis_client import redis_service
from app.services.llm_worker import explain_transaction_task

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load ONNX Model
    logger.info("Initializing system...")
    dl_engine.load_model()
    yield
    # Shutdown: Clean up if needed
    logger.info("Shutting down system...")

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    version="4.0"
)

# --- Endpoints ---

@app.post("/predict", response_model=ImmediateResponse)
async def predict_fraud(request: TransactionRequest):
    transaction_id = str(uuid.uuid4())
    
    # 1. Feature Mapping (23 features total as per new schema)
    inference_input = InferenceFeatures(
        city_pop=request.city_pop,
        hour=request.hour,
        age=request.age,
        unix_time=request.unix_time,
        amt_diff_avg_30d=request.amt_diff_avg_30d,
        trans_count_24h=request.trans_count_24h,
        distance_velocity=request.distance_velocity,
        merchant_risk_score=request.merchant_risk_score,
        merchant_freq_30d=request.merchant_freq_30d,
        cat_misc_net=request.cat_misc_net,
        cat_grocery_pos=request.cat_grocery_pos,
        cat_entertainment=request.cat_entertainment,
        cat_gas_transport=request.cat_gas_transport,
        cat_misc_pos=request.cat_misc_pos,
        cat_grocery_net=request.cat_grocery_net,
        cat_shopping_net=request.cat_shopping_net,
        cat_shopping_pos=request.cat_shopping_pos,
        cat_food_dining=request.cat_food_dining,
        cat_personal_care=request.cat_personal_care,
        cat_health_fitness=request.cat_health_fitness,
        cat_travel=request.cat_travel,
        cat_kids_pets=request.cat_kids_pets,
        cat_home=request.cat_home
    )
    
    # 2. Sync Lane: DL Inference
    score, prediction = dl_engine.predict(inference_input)
    
    # 3. Conditional Gate: Techno-Economic Gating
    explanation_id = None
    app_status = "completed"
    
    if prediction == "Fraud":
        explanation_id = str(uuid.uuid4())
        app_status = "explaining"
        
        # Store pending status in Redis
        redis_service.store_explanation(explanation_id, {"status": "pending", "explanation_id": explanation_id})
        
        # 4. Async Lane: Rule-Based XAI via Celery
        explain_transaction_task.delay(
            explanation_id, 
            score, 
            inference_input.model_dump()
        )
    
    return ImmediateResponse(
        transaction_id=transaction_id,
        score=score,
        prediction=prediction,
        status=app_status,
        explanation_id=explanation_id
    )

@app.get("/explain/{explanation_id}", response_model=ExplanationResponse)
async def get_explanation(explanation_id: str):
    explanation = redis_service.get_explanation(explanation_id)
    
    if not explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Explanation not found"
        )
    
    if explanation.get("status") == "pending":
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Explanation is still being processed"
        )
    
    if explanation.get("status") == "failed":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explanation generation failed: {explanation.get('error')}"
        )
        
    return explanation

@app.post("/config/explanation-mode")
async def set_explanation_mode(request: ModeToggleRequest):
    redis_service.set_explanation_mode(request.mode)
    return {"message": f"Explanation mode updated to {request.mode}"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now(timezone.utc),
        "explanation_mode": redis_service.get_explanation_mode()
    }
