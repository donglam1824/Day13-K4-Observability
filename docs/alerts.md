# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: high_latency_p95
- Severity: warning
- SLI/SLO liên quan: latency_p95_ms objective 3000ms, target 99.5%
- Điều kiện và thời gian duy trì: latency_p95 > 3000ms liên tục trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng trải nghiệm phản hồi chậm, tương tác chat bị trễ và giảm độ mượt mà của workflow.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra dashboard latency để xác định xem P95 tăng do toàn bộ hệ thống hay chỉ một feature cụ thể.
  2. Mở trace Langfuse để kiểm tra waterfall và phân tích xem `retrieve` hay `generate` đang gây ra độ trễ cao.
  3. Xem logs và incident state để tìm dấu hiệu `rag_slow`, model timeout hoặc tắc nghẽn I/O.
- Mitigation tạm thời: Tạm thời giảm tải traffic, giới hạn concurrency hoặc chuyển sang cấu hình model nhẹ hơn để giữ độ trễ trong ngưỡng chấp nhận được.
- Owner: on-call-engineer

## Alert 2

- Tên: elevated_error_rate
- Severity: critical
- SLI/SLO liên quan: error_rate_pct objective 2%, target 99.0%
- Điều kiện và thời gian duy trì: error_rate_pct > 5% liên tục trong 3 phút
- Ảnh hưởng tới người dùng: Người dùng nhận được nhiều lỗi chat, không có câu trả lời hợp lệ hoặc bị thất bại khi gửi yêu cầu.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra charts error rate và breakdown để xác định loại lỗi phổ biến nhất (timeout, model failure, internal exception).
  2. Xem trace chi tiết trong Langfuse để xác định xem lỗi xảy ra tại `retrieve`, `generate` hay bước cập nhật trace.
  3. Kiểm tra logs chi tiết và incident state để tìm stack trace, lỗi service hoặc điều kiện nguồn dữ liệu bị hỏng.
- Mitigation tạm thời: Kích hoạt cơ chế fallback, giới hạn request mới, hoặc rollback thay đổi gần nhất nếu lỗi khởi phát do cập nhật code/config.
- Owner: on-call-engineer

## Alert 3

- Tên: cost_budget_exceeded
- Severity: warning
- SLI/SLO liên quan: daily_cost_usd objective 2.5 USD
- Điều kiện và thời gian duy trì: daily_cost_usd > 2.5 USD trong 1 ngày
- Ảnh hưởng tới người dùng: Chi phí tăng vượt ngân sách, có nguy cơ bị giới hạn dịch vụ hoặc phải tắt bớt tính năng để kiểm soát chi phí.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra dashboard cost và token usage để xác định liệu chi phí tăng do số lượng request hay do token/output bất thường.
  2. Xác định feature, user hoặc model nào tiêu thụ nhiều token nhất và xem trace/metadata để tìm nguyên nhân.
  3. Kiểm tra logs và incidents để xác định spike chi phí do lỗi config, vòng lặp prompt, hoặc output token bùng phát.
- Mitigation tạm thời: Áp dụng giới hạn request, giảm model kích thước, hoặc giới hạn token tối đa để ngăn chi phí tăng thêm.
- Owner: team-lead
