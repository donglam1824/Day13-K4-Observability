# Yêu cầu dashboard

Contract có thể kiểm tra bằng máy nằm tại `config/dashboard.yaml`. Hướng dẫn dựng và kiểm tra runtime nằm tại [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md).

Dashboard chính cần đủ 6 nhóm thông tin:

1. Latency P50/P95/P99.
2. Traffic: request count hoặc QPS.
3. Error rate và breakdown theo loại lỗi.
4. Cost theo thời gian.
5. Tổng token input/output.
6. Quality proxy.

Tiêu chuẩn trình bày:

- Khoảng thời gian mặc định: 1 giờ.
- Tự refresh mỗi 15–30 giây nếu công cụ hỗ trợ.
- Có threshold hoặc SLO line.
- Ghi rõ đơn vị.
- Chỉ giữ 6–8 panel quan trọng ở lớp chính.
- Screenshot phải nhìn được tên panel và khoảng thời gian.

## Dashboard panels

| Panel | Unit | Default time range | Threshold / SLO line | Tool description |
| --- | --- | --- | --- | --- |
| Latency percentiles | ms | 1 hour | P95 ≤ 3000ms | Specification-based contract for Grafana/Langfuse using `latency_p50`, `latency_p95`, `latency_p99` from `/metrics` |
| Request traffic | requests_per_minute | 1 hour | QPS ≥ 1 | Specification-based contract for Grafana/Langfuse using `traffic` from `/metrics` |
| Error rate and breakdown | percent | 1 hour | Error rate ≤ 2% | Specification-based contract for Grafana/Langfuse using `error_rate_pct` and `error_breakdown` from `/metrics` |
| Cost over time | usd | 1 hour | Total cost ≤ 2.5 USD | Specification-based contract for Grafana/Langfuse using `total_cost_usd`, `avg_cost_usd` from `/metrics` |
| Input/output tokens | tokens | 1 hour | N/A (informational trend) | Specification-based contract for Grafana/Langfuse using `tokens_in_total` and `tokens_out_total` from `/metrics` |
| Quality proxy | score_0_to_1 | 1 hour | Mean score ≥ 0.75 | Specification-based contract for Grafana/Langfuse using `quality_avg` from `/metrics` |

## Panel details

- Latency percentiles
  - Panel name: `Latency percentiles`
  - Unit: `ms`
  - Default time range: 1 hour
  - Threshold/SLO line: P95 ≤ 3000ms
  - Tool used: specification-based description; implementable in Grafana or Langfuse.

- Request traffic
  - Panel name: `Request traffic`
  - Unit: `requests_per_minute`
  - Default time range: 1 hour
  - Threshold/SLO line: QPS ≥ 1
  - Tool used: specification-based description; implementable in Grafana or Langfuse.

- Error rate and breakdown
  - Panel name: `Error rate and breakdown`
  - Unit: `percent`
  - Default time range: 1 hour
  - Threshold/SLO line: error_rate_pct ≤ 2%
  - Tool used: specification-based description; implementable in Grafana or Langfuse.

- Cost over time
  - Panel name: `Cost over time`
  - Unit: `usd`
  - Default time range: 1 hour
  - Threshold/SLO line: total_cost_usd ≤ 2.5 USD
  - Tool used: specification-based description; implementable in Grafana or Langfuse.

- Input and output tokens
  - Panel name: `Input and output tokens`
  - Unit: `tokens`
  - Default time range: 1 hour
  - Threshold/SLO line: informational trending panel with cumulative totals
  - Tool used: specification-based description; implementable in Grafana or Langfuse.

- Quality proxy
  - Panel name: `Quality proxy`
  - Unit: `score_0_to_1`
  - Default time range: 1 hour
  - Threshold/SLO line: quality_avg ≥ 0.75
  - Tool used: specification-based description; implementable in Grafana or Langfuse.

Kiểm tra contract trước khi chụp evidence:

```bash
python scripts/validate_dashboard.py
```
