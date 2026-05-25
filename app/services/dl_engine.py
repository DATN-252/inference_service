import onnxruntime as ort
import numpy as np
import os
import logging
from app.config import settings
from app.schemas import InferenceFeatures

logger = logging.getLogger(__name__)

class DLEngine:
    def __init__(self):
        self.session = None
        self.input_name = None

    def load_model(self):
        """Load the ONNX model into memory."""
        if not os.path.exists(settings.MODEL_PATH):
            logger.warning(f"Model file not found at {settings.MODEL_PATH}. Using mock inference.")
            return

        try:
            self.session = ort.InferenceSession(settings.MODEL_PATH)
            self.input_name = self.session.get_inputs()[0].name
            logger.info("ONNX Model Loaded Successfully")
        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")

    def predict(self, features: InferenceFeatures) -> tuple[float, str]:
        """
        Perform inference using ONNX Runtime.
        Returns: (score, prediction)
        """
        if self.session is None:
            # Mock inference if model is missing
            import random
            score = random.uniform(0, 1)
            prediction = "Fraud" if score > 0.5 else "Legit"
            return score, prediction

        # Get raw input and ensure it is float32 for ONNX
        input_data = features.to_numpy_array().astype(np.float32)
        
        # Diagnostic Log: See exactly what is being sent to the model
        logger.info(f"DIAGNOSTIC - Input Vector: {input_data.tolist()}")
        
        outputs = self.session.run(None, {self.input_name: input_data})
        
        try:
            # 1. Extract raw values
            result_array = np.array(outputs[0]).flatten()
            
            # 2. Logic for multi-class vs single-class
            # If model returns [p0, p1], p1 is usually the "Fraud" class.
            raw_val = float(result_array[-1]) 
            
            # 3. Apply Sigmoid Activation (Logit processing)
            score = 1 / (1 + np.exp(-raw_val))
            
            logger.info(f"Inference result - Raw: {raw_val:.4f}, Probability: {score:.4f}, Shape: {result_array.shape}")
            
        except (IndexError, TypeError, ValueError) as e:
            logger.error(f"CRITICAL: Failed to extract score. Content: {outputs}. Error: {e}")
            score = 0.5 
            
        prediction = "Fraud" if score > 0.5 else "Legit"
        return float(score), prediction

dl_engine = DLEngine()
