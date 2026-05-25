import torch
import os
import sys

def export_model(pt_model_path: str, onnx_output_path: str):
    """
    Exports a PyTorch (.pt) model to ONNX format for use in the Inference Service.
    Expected input: 23 numerical features (including one-hot categories).
    """
    
    if not os.path.exists(pt_model_path):
        print(f"ERROR: PyTorch model not found at {pt_model_path}")
        return

    print(f"Loading PyTorch model from {pt_model_path}...")
    try:
        # Load the model (assumes model architecture is saved or weights-only with map_location)
        model = torch.load(pt_model_path, map_location=torch.device('cpu'))
        model.eval()
    except Exception as e:
        print(f"ERROR: Failed to load model: {e}")
        return

    # Create dummy input matching the InferenceFeatures schema (23 features)
    # Shape: (Batch Size 1, 23 Features)
    dummy_input = torch.randn(1, 23)

    print(f"Exporting to ONNX format at {onnx_output_path}...")
    try:
        torch.onnx.export(
            model,
            dummy_input,
            onnx_output_path,
            export_params=True,        # Store trained parameter weights inside the model file
            opset_version=12,          # Standard opset for compatibility
            do_constant_folding=True,  # Optimize by folding constants
            input_names=['input'],     # The name we use in dl_engine.py
            output_names=['output'],    # The output name
            dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}} # Allow dynamic batching
        )
        print("SUCCESS: Model exported successfully.")
        print(f"Place this file in the 'models/' directory of the inference service.")
    except Exception as e:
        print(f"ERROR: Export failed: {e}")

if __name__ == "__main__":
    # Default paths - can be adjusted via command line or modified here
    PT_PATH = "models/fraud_model.pt"
    ONNX_PATH = "models/fraud_model.onnx"
    
    if len(sys.argv) > 1:
        PT_PATH = sys.argv[1]
    if len(sys.argv) > 2:
        ONNX_PATH = sys.argv[2]

    os.makedirs(os.path.dirname(ONNX_PATH), exist_ok=True)
    export_model(PT_PATH, ONNX_PATH)
