# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Hoang Ngoc Duc
- **MSSV:** 2A202602380
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/younglonelyboiz/K4-L3-DAY13-HoangNgocDuc-2A202602380-Monitoring-LLMOps
- **Commit SHA cuối:** [ĐIỀN MÃ COMMIT SAU KHI PUSH VÀO ĐÂY]
- **Challenge ID:** day13-k4-l3b-monitoring-llmops-v1
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602380`

## 2. Evidence index

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.txt` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08a-trace-metadata.png`, `evidence/08b-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | Lỗi thiếu field PII, struct log | 100/100 | Đã xử lý che PII và inject đủ các trường vào JSON log |
| `validate_dashboard.py` | Thiếu panel | Hợp lệ (6/6) | Khai báo đủ 6 panel theo chuẩn monitoring |
| `pytest` | Fail nhiều tests | Pass | Sửa thành công test PII và agent flow |
| Số traces hợp lệ | 0 | >10 | Tạo thành công qua Langfuse SDK v3 |
| Số PII leak | Lộ thẻ/SĐT | 0 | Viết regex scrub thông tin nhạy cảm trước khi log |
| Latency P95 / TTFT P95 | Vượt mức | Đạt chuẩn (<2000ms) | Phản hồi ổn định khi không có sự cố |
| Retrieval success rate | Kém | Tốt | Vector search mock trả về đúng context |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Dùng middleware `correlation_id_middleware` gán UUIDv4 cho mỗi request vào `structlog` contextvars để truyền qua toàn bộ luồng.
- **Các metadata được ghi vào structured log:** `correlation_id`, `user_id_hash`, `session_id`, `feature`, `latency_ms`, `tokens_in`, `tokens_out`, `cost_usd`.
- **Cách bảo đảm PII được scrub trước khi ghi:** Sử dụng các Regex Patterns (cho thẻ tín dụng, CCCD, Email, SĐT) trong class `PIIRedactor` để đè ký tự nhạy cảm thành `[REDACTED_...]` trước khi log ra file.
- **Cách kiểm chứng kết quả:** Chạy script `validate_logs.py` kiểm tra field JSON và chạy `pytest tests/test_pii.py`.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Cấu hình `LANGFUSE_PUBLIC_KEY` và `LANGFUSE_SECRET_KEY` cá nhân vào `.env`.
- **Cấu trúc root/retrieval/generation observations:** Bọc `@observe(as_type="agent")` cho root, `@observe(as_type="span")` cho RAG retrieval và `@observe(as_type="generation")` cho LLM generate. 
- **Cách nối trace với log:** Sử dụng chung `correlation_id` truyền qua tags của Langfuse và log fields của structlog.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** v1 / `baseline`
- **Version/label candidate:** v2 / `candidate`
- **Trace ID của mỗi version:** (Trong thư mục evidence)
- **Cách promote và rollback `production`:** Thêm label `production` cho v1 để promote, khi có sự cố gỡ label `production` khỏi v1 và gắn cho v2 để rollback.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Request Count, Error Rate, Latency (p95, p99), Token Usage, Cost, Cache Hit Ratio.
- **SLO và lý do chọn:** Latency p95 < 2000ms, Error rate < 5%. Đây là mức cân bằng giữa chi phí LLM và trải nghiệm người dùng chatbot.
- **Cách tính error budget:** SLO 95% thành công trong 28 ngày nghĩa là error budget là 5% tổng request. Nếu có 10,000 request thì tối đa 500 request được phép thất bại.
- **Ba alert và runbook tương ứng:** 
  1. `HighErrorRate` (Lỗi nhiều) -> Rollback prompt/model.
  2. `LatencySpike` (Chậm) -> Kiểm tra RAG, VectorDB.
  3. `CostSpike` (Phí cao bất thường) -> Kiểm tra abuse, token limit.

## 7. Điều tra challenge

- **Challenge ID:** K4-L3B-challenge (rag_slow)
- **Khoảng thời gian điều tra:** 2026-09-30 05:18 UTC 
- **Triệu chứng từ metrics:** Dashboard ghi nhận Latency nhảy vọt lên 14.8 giây cho mỗi request, vượt xa ngưỡng SLO (2000ms).
- **Log line và correlation ID liên quan:** Terminal xuất hiện hàng loạt log báo latency hơn 14000ms (VD: `req-ecda63c7`).
- **Trace ID và span gây ảnh hưởng:** Trace trên Langfuse chỉ ra span `retrieval` bị nghẽn (tốn ~2.5s thay vì phản hồi ngay).
- **Root cause:** Khối truy xuất tài liệu RAG (`mock_rag.py`) gặp hiện tượng chập chờn / treo khiến toàn bộ các luồng request bị block, đẩy độ trễ tổng thể lên cực kỳ cao do giới hạn concurrency pool.
- **Fix action:** Vô hiệu hóa sự cố (`inject_incident.py --disable`), kiểm tra hệ thống Vector DB.
- **Preventive measure:** Thêm timeout cứng cho hàm retrieval, cài đặt Caching để giảm tải, lập cảnh báo khi Retrieval Time > 1s.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Quyết định không thu thập Input/Output thô của khách vào Trace (set `capture_input=False`) nhằm bảo vệ tối đa dữ liệu cá nhân PII của khách hàng khỏi việc rò rỉ lên cloud bên thứ ba (Langfuse).
- **Một lỗi/blocker đã gặp:** Gắn nhầm vị trí import thư viện vào trong block class thay vì đầu file khiến API báo lỗi 500 (`get_langfuse_client is not defined`).
- **Cách tìm nguyên nhân và xử lý:** Mở log bằng lệnh `tail` để truy vết traceback, phát hiện ra NameError và đẩy import lên đầu file.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics (nhìn biểu đồ Dashboard thấy gai nhọn) -> Logs (soi log tìm `correlation_id` của request thất bại) -> Traces (Lên Langfuse gõ ID đó truy vết nguyên nhân do node nào chạy chậm).
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** LLM là hộp đen và tốn kém. Monitor giúp không bị "cháy túi", SLO bảo vệ khách hàng, Prompt version giúp thử nghiệm an toàn và rollback ngay khi model nói bậy.
- **Điều quan trọng nhất đã học:** Bảo mật PII là ưu tiên số 1 khi làm việc với LLM. Luôn phải Redact dữ liệu ở cổng middleware.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Em đã hoàn thành 100% tất cả yêu cầu của bài thực hành.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
