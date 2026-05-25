Dưới đây là bảng phân rã công việc (Work Breakdown Structure) được tinh chỉnh cho lộ trình phát triển độc lập. Các tác vụ này tuân thủ tuyệt đối hệ sinh thái Pure Python, triết lý thiết kế tối giản và tư duy phòng ngự từ xa (Prophylaxis) để bảo vệ hiệu năng.

## Giai đoạn 1: Foundation & Gateway (Hợp đồng Dữ liệu)

**Task 1.1: Thiết lập Workspace và API Gateway**

* **Yêu cầu:** Khởi tạo project với FastAPI và Pydantic v2. Thiết lập môi trường IDE tối giản để tập trung toàn lực vào luồng dữ liệu. Định nghĩa chính xác các schema: `TransactionRequest`, `ImmediateResponse`, và `ExplanationResponse`. Thiết lập endpoint `/predict` với kết quả giả lập (Mock).
* **Output Nghiệm thu:** Ứng dụng khởi động thành công bằng `uvicorn`. Truy cập Swagger UI hiển thị đầy đủ tài liệu API. Bắn một request sai kiểu dữ liệu phải bị Pydantic chặn lại ngay lập tức (HTTP 422 Unprocessable Entity).

**Task 1.2: Thiết lập In-memory Cache & Quản lý Trạng thái**

* **Yêu cầu:** Chạy một Redis container thông qua Docker. Tích hợp `redis-py` vào FastAPI. Viết hai hàm tiện ích: một hàm kéo (pull) features dựa trên `user_id`, một hàm đẩy (push) kết quả giải thích kèm TTL (Time-To-Live).
* **Output Nghiệm thu:** Script test kết nối Redis thành công. Endpoint `/predict` có thể đọc log hiển thị "Cache Hit" hoặc "Cache Miss" khi nhận request.

---

## Giai đoạn 2: Lõi Động cơ Deep Learning (The Engine)

**Task 2.1: Chuyển đổi và Tích hợp ONNX Runtime**

* **Yêu cầu:** Cài đặt `onnxruntime`. Chuyển đổi file trọng số mô hình đang có sang định dạng `.onnx`. Thiết lập logic nạp mô hình vào bộ nhớ một lần duy nhất tại sự kiện ứng dụng khởi động (`lifespan` hoặc `@app.on_event("startup")`). Tuyệt đối không nạp lại mô hình trên mỗi request.
* **Output Nghiệm thu:** Terminal in ra log "ONNX Model Loaded Successfully" khi khởi động.

**Task 2.2: Thay thế Mock Data bằng Real Inference**

* **Yêu cầu:** Kết nối dữ liệu từ Redis nạp thẳng vào ma trận đầu vào của `onnxruntime`. Nhận kết quả `score` và `prediction` thực tế, chuyển đổi kiểu dữ liệu tương thích với Pydantic và trả về cho Client.
* **Output Nghiệm thu:** Endpoint `/predict` trả về kết quả toán học chính xác từ file `.onnx`. Đo đạc độ trễ (Latency) trả về trên Postman/Swagger phải nhỏ hơn 50ms.

---

## Giai đoạn 3: Phân luồng & Cổng Kinh tế (Techno-Economic Gating)

**Task 3.1: Triển khai Cổng kiểm soát (Conditional Gate)**

* **Yêu cầu:** Thiết lập biến môi trường cấu hình ngưỡng rủi ro (ví dụ: `RISK_THRESHOLD = 0.85`). Viết logic chặn: Nếu `score` từ ONNX trả về thấp hơn ngưỡng, gán `status="completed"` và kết thúc. Nếu cao hơn hoặc bằng ngưỡng, gán `status="explaining"` và sinh ra một chuỗi `explanation_id`.
* **Output Nghiệm thu:** Gửi hai request test khác nhau. Request có rủi ro thấp không sinh ra `explanation_id`. Request có rủi ro cao trả về một `explanation_id` hợp lệ.

**Task 3.2: Tách luồng Bất đồng bộ (Async Background Task)**

* **Yêu cầu:** Tích hợp `BackgroundTasks` của FastAPI. Tạo một hàm Worker chạy ngầm chứa lệnh `time.sleep(3.0)` để giả lập độ trễ của LLM. Kích hoạt hàm này chỉ khi request vượt qua Cổng kiểm soát ở Task 3.1.
* **Output Nghiệm thu:** Client nhận được response của luồng Sync ngay lập tức (< 50ms). Terminal tiếp tục chạy ngầm và in ra log "[Async] Đã hoàn thành giải thích" sau 3 giây mà không làm treo Gateway.

---

## Giai đoạn 4: Tích hợp Lõi Ngôn ngữ (The Brain) & End-to-End

**Task 4.1: Xây dựng LLM Worker & Prompt Engineering**

* **Yêu cầu:** Thay thế `time.sleep` bằng lệnh gọi thực tế tới LLM (API hoặc Local). Nạp `score` và top features vào Prompt Template. Ép LLM trả về đúng định dạng JSON cấu trúc hóa. Lưu kết quả này vào Redis với key là `explanation_id` đã sinh ra ở Giai đoạn 3.
* **Output Nghiệm thu:** Kiểm tra database Redis sau khi luồng Async chạy xong, dữ liệu JSON của lời giải thích phải tồn tại và đúng cấu trúc của schema `ExplanationResponse`.

**Task 4.2: Hoàn thiện Polling Endpoint cho Client**

* **Yêu cầu:** Viết thêm endpoint GET `/explain/{explanation_id}` trên FastAPI để Client có thể truy vấn lấy lời giải thích sau khi nhận được cảnh báo từ luồng Sync. Xử lý gọn gàng trường hợp lời giải thích vẫn đang được tạo (HTTP 202 Accepted) hoặc không tìm thấy (HTTP 404 Not Found).
* **Output Nghiệm thu:** Kịch bản End-to-End: Bắn POST `/predict` -> Nhận `explanation_id` lập tức -> Bắn GET `/explain/{id}` ngay lập tức nhận mã 202 -> Chờ 3 giây bắn lại GET `/explain/{id}` nhận được cục JSON chứa nguyên nhân rủi ro chi tiết. Toàn bộ kiến trúc vận hành thông suốt trên một process.