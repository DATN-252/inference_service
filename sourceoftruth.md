# 📄 SOURCE OF TRUTH: MINIMALIST ML INFERENCE SERVICE

**Phiên bản:** 4.0 (Enterprise AI Platform)
**Triết lý cốt lõi:** Spatial Topology (Tối ưu không gian dữ liệu bộ nhớ), Minimalist Design (Triệt tiêu độ trễ mạng chéo), và Fault Tolerance (Khả năng chịu lỗi bền bỉ).

---

## 1. MÔ TẢ DỰ ÁN (PROJECT DESCRIPTION)

Dự án xây dựng một hệ thống **Inference Service phân luồng kép (Dual-lane)**, kết hợp khả năng dự đoán cực nhanh của Deep Learning (DL) và khả năng giải thích minh bạch của Rule-Based Explainable AI (XAI).

Hệ thống áp dụng tư duy topology phẳng để tối ưu hiệu suất, đồng thời gia cố độ tin cậy bằng hàng đợi công việc bất đồng bộ.

* **Sync Lane (Luồng Đồng bộ):** Xử lý Real-time Prediction. Sử dụng ONNX Runtime để thực thi mô hình Deep Learning ngay trong process của Gateway, đảm bảo phản hồi tức thì cho các ứng dụng nhạy cảm với độ trễ.
* **Async Lane (Luồng Bất đồng bộ):** Xử lý Rule-Based XAI. Các giao dịch có rủi ro cao sẽ được đẩy vào hàng đợi Celery để phân tích nguyên nhân gốc rễ một cách bền bỉ và tách biệt khỏi luồng chính.

---

## 2. YÊU CẦU KỸ THUẬT (TECHNICAL REQUIREMENTS)

### 2.1. Yêu cầu về Hiệu năng (Performance Constraints)

* **Prediction Latency (P99):** Dưới **50ms**.
* **Explanation Latency:** Xử lý gần như tức thì (Near-instant) sau khi task được worker tiếp nhận, nhờ loại bỏ hoàn toàn độ trễ của các mô hình ngôn ngữ lớn (LLM).
* **Throughput:** Khả năng mở rộng ngang (Horizontal Scaling) nhờ kiến trúc Celery Workers.

### 2.2. Yêu cầu về Độ tin cậy (Resilience & Prophylaxis)

* **Resilient Queue:** Sử dụng Redis làm Broker để đảm bảo task không bị mất khi hệ thống restart (At-least-once delivery).
* **Techno-Economic Gating:** Chỉ kích hoạt giải thích XAI khi điểm số rủi ro vượt ngưỡng cấu hình (`RISK_THRESHOLD`), bảo vệ tài nguyên tính toán của Worker.
* **Fail-safe Extraction:** Cơ chế phòng ngự (Prophylaxis) trong lõi DL để xử lý các sai lệch về output shape của mô hình mà không làm sập Gateway.

### 2.3. Yêu cầu về Tính toàn vẹn Dữ liệu (System Integrity)

* **Strict Data Contracts:** 100% Request tuân thủ chính xác schema `request.json` thông qua Pydantic v2.
* **Timezone Awareness:** Toàn bộ log và timestamp hệ thống sử dụng chuẩn UTC để đảm bảo tính nhất quán trên các server phân tán.

---

## 3. CÔNG NGHỆ SỬ DỤNG (TECHNOLOGY STACK)

### 3.1. Lõi Điều phối & Giao tiếp (Orchestration & Validation)

* **FastAPI:** ASGI Framework tốc độ cao, quản lý định tuyến và giao tiếp Client.
* **Pydantic (v2):** Ép kiểu dữ liệu và rà soát schema tự động.
* **Celery:** Hệ thống quản lý hàng đợi công việc (Distributed Task Queue) cho luồng giải thích.

### 3.2. Lõi Tính toán Deep Learning (The Engine)

* **ONNX Runtime:** Động cơ thực thi mô hình tối ưu hóa cho CPU, tận dụng C++ backend để đạt độ trễ cực thấp.

### 3.3. Lõi Quản lý Trạng thái & Hàng đợi (State & Cache)

* **Redis:** Đóng vai trò Broker cho Celery và In-memory Store để lưu trữ kết quả giải thích kèm cơ chế TTL.

### 3.4. Lõi Giải thích AI (Explainable AI)

* **Rule-Based XAI Engine:** Hệ thống suy luận dựa trên luật toán học (Mathematical Rules), phân tích trực tiếp các đặc trưng đầu vào để tìm ra các drivers gây rủi ro chính, thay thế hoàn toàn LLM để đạt tốc độ và tính kinh tế tối đa.
