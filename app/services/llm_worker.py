import logging
import requests
from datetime import datetime, timezone
from typing import List, Tuple

from app.celery_app import celery_app
from app.services.redis_client import redis_service

logger = logging.getLogger(__name__)

class RuleBasedExplainer:
    """
    Deterministic Explainable AI (XAI) Engine.
    Uses mathematical rules to identify risk drivers and generate explanations.
    """
    
    # Define baseline thresholds for risk detection
    THRESHOLDS = {
        "distance_velocity": 80.0,      # km/h
        "trans_count_24h": 10,          # count
        "amt_diff_avg_30d": 50.0,       # absolute deviation
        "merchant_risk_score": 0.05,    # probability
        "merchant_freq_30d": 15         # frequency
    }

    @classmethod
    def analyze(cls, score: float, features: dict) -> Tuple[List[str], str, str]:
        """
        Analyzes features and generates top factors and a natural language explanation.
        """
        top_factors = []
        risk_descriptions = []
        
        # 1. Evaluate specific drivers
        if features.get("distance_velocity", 0) > cls.THRESHOLDS["distance_velocity"]:
            val = features["distance_velocity"]
            top_factors.append("Abnormal Transaction Velocity")
            risk_descriptions.append(f"unusually high movement speed ({val:.1f} km/h) between transactions")

        if features.get("trans_count_24h", 0) > cls.THRESHOLDS["trans_count_24h"]:
            val = features["trans_count_24h"]
            top_factors.append("High Transaction Frequency")
            risk_descriptions.append(f"a high volume of transactions ({val}) within a 24-hour window")

        if features.get("amt_diff_avg_30d", 0) > cls.THRESHOLDS["amt_diff_avg_30d"]:
            val = features["amt_diff_avg_30d"]
            top_factors.append("Spending Pattern Deviation")
            risk_descriptions.append(f"a significant deviation (${val:.2f}) from the 30-day average spending")

        if features.get("merchant_risk_score", 0) > cls.THRESHOLDS["merchant_risk_score"]:
            val = features["merchant_risk_score"]
            top_factors.append("High-Risk Merchant Association")
            risk_descriptions.append(f"association with a merchant having a high historical fraud rate ({val*100:.1f}%)")

        # 2. Determine Risk Level
        risk_level = "Critical" if score >= 0.95 else "High"
        
        # 3. Construct Natural Language Explanation
        if not risk_descriptions:
            top_factors = ["Aggregate Risk Correlation"]
            explanation = (
                f"The transaction was flagged with a {risk_level} risk score of {score:.2f} due to "
                "multiple borderline anomalies across behavioral and temporal features that, "
                "when combined, correlate strongly with known fraud signatures."
            )
        else:
            factors_joined = " and ".join(risk_descriptions[:3])
            explanation = (
                f"The transaction was flagged with a {risk_level} risk score of {score:.2f} primarily due to "
                f"{factors_joined}. This pattern deviates significantly from established user baselines."
            )

        return top_factors, explanation, risk_level

class NLPExplainer:
    """
    NLP-based Explanation Engine using local llama-cpp-python.
    Loads the specific GGUF model provided by the user.
    """
    _model = None
    MODEL_PATH = "models/qwen2.5-1.5b-instruct-q4_k_m-00001-of-00001.gguf"

    @classmethod
    def _get_model(cls):
        if cls._model is None:
            from llama_cpp import Llama
            import os
            if not os.path.exists(cls.MODEL_PATH):
                logger.error(f"NLP Model not found at {cls.MODEL_PATH}")
                return None
            
            logger.info(f"Loading NLP Model (Performance Mode): {cls.MODEL_PATH}")
            cls._model = Llama(
                model_path=cls.MODEL_PATH,
                n_ctx=1024,      # Optimized context window for speed
                n_threads=8,     # Increased threads for multi-core CPUs
                n_batch=512,     # Standard batch size
                use_mlock=True,  # Keep model in RAM (avoids disk swap latency)
                verbose=False
            )
        return cls._model

    @classmethod
    def analyze(cls, score: float, features: dict) -> str:
        model = cls._get_model()
        if model is None:
            return None

        # Polite customer-centric prompt for end-user communication
        prompt = f"""<|im_start|>system
Polite Banking Security Assistant. Features: {features}
Informing a customer about a security check as a helpful safety measure. 
Write 2 polite sentences explaining the unusual activity (e.g. timing or amount) without using numbers or technical terms.<|im_end|>
<|im_start|>user
Provide a polite security update for the customer.<|im_end|>
<|im_start|>assistant
"""
        try:
            output = model(
                prompt,
                max_tokens=100,      # Hard limit to enforce conciseness
                stop=["<|im_end|>"],
                temperature=0.1,
                echo=False
            )
            return output['choices'][0]['text'].strip()
        except Exception as e:
            logger.warning(f"NLP Engine (llama-cpp) failed: {e}. Falling back to Rule-Based XAI.")
            return None

@celery_app.task(name="app.services.llm_worker.explain_transaction_task")
def explain_transaction_task(explanation_id: str, score: float, features: dict):
    """
    Dual-Engine Celery Task: Rule-Based fallback + NLP (Qwen).
    """
    logger.info(f"[Dual-Engine] Starting analysis for {explanation_id}")
    
    # 1. Get current explanation mode
    mode = redis_service.get_explanation_mode()
    
    # Always compute Rule-Based factors for the 'top_factors' list
    rule_factors, rule_exp, risk_level = RuleBasedExplainer.analyze(score, features)
    
    final_explanation = rule_exp
    
    # 2. If NLP mode is enabled, try to get rich explanation
    if mode == "nlp":
        nlp_exp = NLPExplainer.analyze(score, features)
        if nlp_exp:
            final_explanation = nlp_exp

    try:
        explanation_data = {
            "explanation_id": explanation_id,
            "status": "completed",
            "score": score,
            "top_factors": rule_factors,
            "natural_language_explanation": final_explanation,
            "risk_level": risk_level,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        redis_service.store_explanation(explanation_id, explanation_data)
        logger.info(f"[Dual-Engine] Analysis completed ({mode}) and stored for {explanation_id}")
        
    except Exception as e:
        logger.error(f"[Dual-Engine] Error: {e}")
        error_data = {"explanation_id": explanation_id, "status": "failed", "error": str(e)}
        redis_service.store_explanation(explanation_id, error_data)
