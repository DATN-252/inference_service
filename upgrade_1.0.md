# 🚀 UPGRADE PLAN: V3.0 TO V4.0 (ENTERPRISE AI PLATFORM)

Bản nâng cấp này giữ nguyên triết lý "Minimalist" nhưng mở rộng sức chịu tải (Fault Tolerance) và khả năng quan sát (Observability), đưa hệ thống từ cấp độ "chạy được" lên cấp độ "không thể sập".

## Lộ trình Nâng cấp (T-Shaped Architect Expansion)

### Cấp độ 1: Gia cố Lõi Bất đồng bộ (Resilient Async Queue)
*Nút thắt hiện tại:* `BackgroundTasks` của FastAPI lưu job trong RAM. Nếu container bị restart đột ngột, toàn bộ lời giải thích đang chờ xử lý sẽ bốc hơi.
* **Hành động:** Chuyển đổi sang **Celery + Redis Broker**.
* **Topology mới:** FastAPI chỉ làm nhiệm vụ đẩy `task_id` vào Redis Stream. Một cluster các Celery Workers chạy ở process khác sẽ consume queue này. Đảm bảo tính chất "At-least-once delivery" (không rớt bất kỳ job giải thích nào).

### Cấp độ 2: Tối ưu Hóa Lõi Ngôn Ngữ (LLM Engine)
*Nút thắt hiện tại:* Gọi API ngoài (OpenAI) tốn kém và phụ thuộc network.
* **Hành động:** Self-host mô hình ngôn ngữ mã nguồn mở (như Llama-3-8B-Instruct) bằng **vLLM**.
* **Tối ưu Kinh tế:** vLLM áp dụng PagedAttention giúp quản lý VRAM cực kỳ tối ưu, cho phép Continuous Batching để sinh hàng loạt lời giải thích cùng lúc với throughput gấp 3-5 lần HuggingFace mặc định.

### Cấp độ 3: Khả năng Quan sát Không gian (Observability & Model Drift)
*Nút thắt hiện tại:* Console logging không đủ để tracking sức khỏe mô hình theo thời gian thực.
* **Hành động:** Tích hợp **Prometheus + Grafana**.
* **Metrics cần đo đạc:**
    1.  *Data Drift:* Phân phối của `distance_velocity` hôm nay có lệch so với tuần trước không? (Cảnh báo retraining).
    2.  *Latency Boxplot:* Đo đạc p50, p95, p99 của luồng Sync.
    3.  *Economic Metrics:* Số tiền API tiết kiệm được nhờ chặn lại ở Cổng `RISK_THRESHOLD`.

### Cấp độ 4: Tăng tốc Lõi Tensor (GPU Acceleration)
*Nút thắt hiện tại:* `onnxruntime` đang chạy trên CPU/Memory mặc định.
* **Hành động:** Re-compile file `.onnx` sang **TensorRT engine** (`.trt`).
* **Kiến trúc:** Ép kiểu dữ liệu (Quantization) từ FP32 xuống FP16 hoặc INT8. Thời gian dự đoán sẽ giảm từ ~20ms xuống còn < 2ms trên GPU NVIDIA, dọn đường cho việc xử lý hàng chục ngàn TPS (Transactions Per Second).