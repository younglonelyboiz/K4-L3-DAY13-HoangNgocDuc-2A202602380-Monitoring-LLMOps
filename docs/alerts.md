# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn bình thường để nhận phản hồi từ LLM
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard để xác định phần trăm tăng của P95/P99 latency
  2. Lọc `data/logs.jsonl` để lấy `correlation_id` của request có độ trễ lớn
  3. Tra cứu `correlation_id` trên Langfuse để xem span nào (retrieval hay LLM generation) đang gây nghẽn
- Mitigation tạm thời: Tạm thời vô hiệu hóa tính năng (feature flag) liên quan hoặc giảm timeout của retrieval/LLM để fail-fast và retry.
- Owner: `student-2A202602380`

## Alert 2

- Tên: `HighErrorRate`
- Severity: `critical`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Tỷ lệ lỗi trên tổng request `error_rate_pct`
- Điều kiện và thời gian duy trì: `error_rate_pct > 2%` trong 5 phút
- Ảnh hưởng tới người dùng: Một số lượng lớn người dùng sẽ nhận được phản hồi lỗi hoặc không thể sử dụng tính năng Chat
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard errors để xem có mã lỗi nào đang gia tăng đột biến
  2. Xem logs để tìm ra message chi tiết của error và tra cứu `correlation_id` tương ứng
  3. Kiểm tra xem sự cố do Vector DB (retrieval) hay LLM API (generation)
- Mitigation tạm thời: Rollback phiên bản prompt/code vừa deploy hoặc kích hoạt mạch ngắt (circuit breaker) nếu do lỗi external API.
- Owner: `student-2A202602380`

## Alert 3

- Tên: `CostSpike`
- Severity: `warning`
- Duration: `15m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Tổng chi phí `total(cost_usd)`
- Điều kiện và thời gian duy trì: `total(cost_usd) > 2.5` trong 15 phút
- Ảnh hưởng tới người dùng: Không trực tiếp, nhưng doanh nghiệp sẽ phải trả chi phí lớn bất thường, có thể dẫn tới vượt ngân sách
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard tokens để xem nguyên nhân chi phí đến từ input tokens (lỗi prompt quá dài) hay output tokens (model trả lời lặp từ)
  2. So sánh logs theo thời gian để xem sự gia tăng xuất hiện từ khi nào
  3. Quan sát các requests và xem xét user nào (hoặc IP nào) gửi request liên tục (bot/DDoS)
- Mitigation tạm thời: Áp dụng rate limiting ở mức thấp hơn, kích hoạt cơ chế chặn theo user/IP, chuyển prompt về phiên bản ngắn gọn hơn.
- Owner: `student-2A202602380`
