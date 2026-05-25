# 🛡️ Minimalist ML Inference Service (v4.0)

An ultra-high-performance, resilient, and minimalist ML Inference Service for Real-time Fraud Detection. Featuring **Dual-Lane Processing**, **Rule-Based XAI**, and **Local NLP Explanations**.

## 🚀 Key Features
- **Sync Lane (<50ms):** High-speed inference using **ONNX Runtime**.
- **Async Lane:** Fault-tolerant background processing using **Celery + Redis**.
- **Dual-Engine XAI:** Switch between deterministic **Rule-Based** reasoning and rich **Local NLP** (Qwen2.5) explanations.
- **Pure Python Ecosystem:** No heavy frameworks, no external API dependencies (optional).
- **Techno-Economic Gating:** Intelligent thresholding to save compute resources.

---

## 🛠️ Prerequisites
- **OS:** Linux or Windows (WSL2 recommended)
- **Python:** 3.10+
- **Docker:** Required for Redis infrastructure

---

## 📦 Setup & Installation

### 1. Environment Setup
Create a virtual environment and install optimized dependencies:
```bash
make install
```

### 2. Infrastructure
Start the Redis broker and cache:
```bash
make redis-up
```

### 3. Model Preparation
The system expects models in the `models/` directory.
- **DL Model:** `models/fraud_model.onnx` (23 features).
- **NLP Model:** `models/qwen2.5-1.5b-instruct-q4_k_m-00001-of-00001.gguf`.

If you have a PyTorch model, use the utility script:
```bash
pip install torch
python3 export_onnx.py models/your_model.pt models/fraud_model.onnx
```

---

## 🏃 Execution

You need to run the API and the Worker in separate terminals:

**Terminal A: The API Gateway**
```bash
make api
```
*Access Documentation at: http://localhost:8000/docs*

**Terminal B: The XAI Worker**
```bash
make worker
```

---

## 📡 API Usage

### Real-time Prediction
`POST /predict`
Submit a transaction following the `request.json` schema.

### Dynamic Explanation Mode
`POST /config/explanation-mode`
Toggle between `rule_based` (deterministic) and `nlp` (rich language).
```bash
curl -X POST http://localhost:8000/config/explanation-mode -d '{"mode": "nlp"}' -H "Content-Type: application/json"
```

### Fetch Explanation
`GET /explain/{explanation_id}`
Retrieve the detailed security analysis for high-risk flags.

---

## 🏗️ Architecture
- **FastAPI:** Orchestration & Validation
- **ONNX Runtime:** Deep Learning Core
- **Redis:** Task Broker & Results Cache
- **Celery:** Background Worker Cluster
- **llama-cpp-python:** Local GGUF Model Hosting

---

## 🧹 Cleanup
To purge cache and temporary files:
```bash
make clean
```
