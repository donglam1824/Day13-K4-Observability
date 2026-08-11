# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Day13-K4-Observability
- Repository URL: https://github.com/donglam1824/Day13-K4-Observability     
- Commit SHA cuối: hiện tại chưa tạo commit mới; dùng trạng thái workspace hiện hành
- Thành viên và vai trò: 
Cáp Việt Anh - 2A202601270 (Tech Lead/Backend Engineer): Phụ trách CP1 (Xây dựng Middleware, gán Correlation ID, Enrichment logs).
Lê Anh Quốc - 2A202601740 (SRE & Alerts Engineer): Phụ trách CP2 (Cấu hình Langfuse, thiết lập SLO/Alert Rules, viết tài liệu Alert Runbook).
Đồng Phúc Lâm - 2A202601902 (QA & Chief Investigator): Thiết kế Dashboard Spec, thực hiện load test, quản lý Challenge/Practice Incident (CP3) và tổng hợp báo cáo nhóm.
## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: đã chạy và qua kiểm tra với unique correlation IDs và log schema hợp lệ
- Tổng số traces: 5 trace được lưu trong [submission/evidence/langfuse_traces.json](evidence/langfuse_traces.json)
- Số PII leak còn lại: 0 trong evidence đã nộp, các dữ liệu nhạy cảm đã được redact bằng placeholder
- Link/đường dẫn dashboard: [config/dashboard.yaml](../config/dashboard.yaml) và [docs/dashboard-spec.md](../docs/dashboard-spec.md)

## 3. Logging và tracing

- Evidence correlation ID: ví dụ req-79ee2f90, req-54ffc607, req-379edc34, req-db1e10bf, req-f22d476a, req-f9a2dd7d, req-05fec93e, req-18a2d08b, req-ee6b3f99, req-f7340352 từ [data/logs.jsonl](../data/logs.jsonl)
- Evidence PII redaction: [submission/evidence/REDACTED EMAIL,CREDITCARD,ETC.png](evidence/REDACTED%20EMAIL,CREDITCARD,ETC.png)
- Evidence trace waterfall: [submission/evidence/langfuse_waterfall.json](evidence/langfuse_waterfall.json)
- Giải thích một span đáng chú ý: span `run` là span cha chính; `generate` và `retrieve` được thể hiện như các sub-span để phân tích thời gian xử lý và nguyên nhân chậm

## 4. Prompt versioning

- Prompt name: day13-chat
- Version/label baseline: production
- Version/label candidate: candidate
- Trace ID của mỗi version: trace evidence đã được lưu trong [submission/evidence/langfuse_traces.json](evidence/langfuse_traces.json)
- Bằng chứng đổi label hoặc rollback: hệ thống hỗ trợ prompt versioning thông qua biến môi trường `LANGFUSE_PROMPT_NAME` và `LANGFUSE_PROMPT_LABEL` theo [app/prompt_management.py](../app/prompt_management.py)

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: hợp lệ, 6/6 panel đúng theo contract
- Evidence dashboard: [config/dashboard.yaml](../config/dashboard.yaml) và [docs/dashboard-spec.md](../docs/dashboard-spec.md)
- SLO đã chọn và lý do: SLO dùng latency P95 ≤ 3000ms, error rate ≤ 2%, daily cost ≤ 2.5 USD và quality score ≥ 0.75 để phản ánh trải nghiệm người dùng và kiểm soát chi phí
- Alert rules và runbook: [config/alert_rules.yaml](../config/alert_rules.yaml) và [docs/alerts.md](../docs/alerts.md)

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1` (Cohort K4)
- Triệu chứng từ metrics: Khi chạy challenge load test (`python scripts/load_test.py --challenge --concurrency 5`), Latency P95 tăng vọt từ ~1.2s lên tới **14.3s – 17.9s (17,914ms)**, vượt xa ngưỡng SLO P95 ≤ 3000ms (~6 lần).
- Trace ID / Correlation ID liên quan: `req-5a084682`, `req-6d93d8c2`, `req-0b5047e6`, `req-dfb311ab`, `req-4da03841`. Trong cây trace, span `retrieve` của RAG bị nghẽn thời gian kéo dài.
- Log line/correlation ID liên quan: Các log record trong `data/logs.jsonl` có `correlation_id` thuộc nhóm `req-6d93d8c2` ghi nhận event `response_sent` với `latency_ms: 17913`.
- Root cause: Sự cố `rag_slow` bị kích hoạt trong `app/incidents.py`, dẫn đến hàm `retrieve()` trong [`app/mock_rag.py`](../app/mock_rag.py#L19-L20) bị delay giả lập `time.sleep(2.5)` trên mỗi truy vấn, gây ra hiện tượng nghẽn hàng chờ khi xử lý đồng thời.
- Fix action: 
  1. Tắt sự cố bằng lệnh `python scripts/inject_incident.py --disable`.
  2. Bổ sung cơ chế Timeout (tối đa 1.5s) và Cache cho kết quả truy vấn RAG trong `retrieve()`.
- Preventive measure:
  1. Cấu hình Alert Rule cho Latency P95 của span `retrieve` > 2000ms trong 2 phút liên tục.
  2. Áp dụng Circuit Breaker: Khi module RAG bị quá tải/chậm, tự động chuyển sang Fallback answer để bảo đảm tổng latency API luôn ≤ 3000ms.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nhóm | Logging, tracing, dashboard contract, SLO/alert runbook và submission evidence | Chưa tạo PR | Hiểu cách metrics, traces và logs liên kết để điều tra incident |
