# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Day13-K4-Observability
- Repository URL: D:\VINNO\Day13-K4-Observability
- Commit SHA cuối: hiện tại chưa tạo commit mới; dùng trạng thái workspace hiện hành
- Thành viên và vai trò: nhóm thực hiện đầy đủ các phần logging, tracing, dashboard contract và report

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

- Challenge ID: Day 13 observability challenge
- Triệu chứng từ metrics: latencies ở mức ~1.1s, cost và token tăng theo request, quality score ổn định ở 0.8-0.9
- Trace ID liên quan: 733ff72e0f614c50e13d5740cdfc0875 và các trace tương ứng trong [submission/evidence/langfuse_traces.json](evidence/langfuse_traces.json)
- Log line/correlation ID liên quan: các correlation ID ở [data/logs.jsonl](../data/logs.jsonl)
- Root cause: hệ thống đang chạy đúng luồng metrics → traces → logs; issue chính là cần có dashboard/SLO/alert rules và evidence trace để hỗ trợ điều tra và cảnh báo
- Fix action: hoàn thiện dashboard contract, SLO và runbook; lưu evidence trace và logs redact
- Preventive measure: tiếp tục theo dõi latency, error rate và chi phí thông qua dashboard và alert rules định kỳ

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nhóm | Logging, tracing, dashboard contract, SLO/alert runbook và submission evidence | Chưa tạo PR | Hiểu cách metrics, traces và logs liên kết để điều tra incident |
