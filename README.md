# VoiceOfCustomer (VoC)

Công cụ dòng lệnh phân tích phản hồi khách hàng bất động sản bằng Gemini: phân loại chủ đề và cảm xúc từng phản hồi, thống kê theo dự án, viết bản nháp insight và hỏi đáp trên kết quả.

Đây mới là phần lõi phân tích chạy trên dữ liệu mẫu. So với đề bài, repo **chưa có**: thu thập từ các kênh thật, embedding và gom cụm, phát hiện điểm nóng, LangGraph, vector database, FastAPI, dashboard Next.js, quy trình duyệt (HITL) và cấu hình Docker/Fly.io. Chi tiết ở [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md), kế hoạch làm tiếp ở [docs/SPRINT_PLAN.md](docs/SPRINT_PLAN.md).

## Cài đặt

Cần Python 3.12.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt        # chỉ để chạy
pip install -r requirements-dev.txt    # thêm pytest và ruff
Copy-Item .env.example .env            # rồi điền GEMINI_API_KEY
```

Các biến tùy chọn (model cho từng tác vụ, timeout, số lần thử lại, đường dẫn dữ liệu) được liệt kê trong [.env.example](.env.example); giá trị mặc định nằm ở [src/config.py](src/config.py).

## Chạy

```powershell
# 1. Che PII, phân loại từng phản hồi, lưu outputs/analysis_report.json
python -m src analyze
python -m src analyze --input data\mock_feedback.json --output outputs\analysis_report.json

# 2. In thống kê theo dự án từ báo cáo đã lưu (không gọi LLM)
python -m src summary

# 3. Như trên, kèm bản nháp insight do LLM viết cho một dự án
python -m src summary --project DuAnA

# 4. Hỏi đáp về kết quả phân tích; nhập "thoat" để kết thúc
python -m src chat
python -m src --verbose chat           # in cả kết quả đầy đủ của từng tool
```

Lệnh 1, 3 và 4 gọi Gemini nên cần `GEMINI_API_KEY`. Lệnh 2–4 đọc báo cáo do lệnh 1 tạo ra.

## Dữ liệu đầu vào và đầu ra

File đầu vào là một danh sách JSON. Mỗi phản hồi gồm:

| Trường | Bắt buộc | Ghi chú |
| --- | --- | --- |
| `id` | Có | Duy nhất trong file; dùng để truy vết bằng chứng |
| `project` | Có | Tên dự án |
| `source` | Có | `crm`, `survey` hoặc `social` |
| `text` | Có | Nội dung phản hồi |
| `customer_name` | Không | Chỉ dùng để che tên trong `text`; không gửi tới LLM, không ghi vào báo cáo |
| `expected_topic`, `expected_sentiment` | Không | Nhãn đúng; có thì báo cáo ghi thêm kết quả so khớp |

Bản ghi sai cấu trúc hoặc trùng `id` bị loại và được ghi vào mục `errors` của báo cáo; lượt chạy vẫn tiếp tục.

Báo cáo `outputs/analysis_report.json` có dạng `{"results": [...], "errors": [...]}`. Mỗi kết quả giữ `id`, `project`, `source`, `text` (bản đã che PII), `analysis` (`topic`, `sentiment`, `evidence`) và `evaluation` (hoặc `null` nếu phản hồi không có nhãn). Thư mục `outputs/` không được đưa vào Git.

Bảy chủ đề: `price`, `construction_progress`, `amenities`, `location_infrastructure`, `legal_process`, `sales_service`, `other`. Ba cảm xúc: `positive`, `negative`, `neutral`. Danh sách này chỉ khai báo một lần trong [src/schemas.py](src/schemas.py); định nghĩa từng chủ đề nằm trong prompt ở [src/prompts.py](src/prompts.py). Chủ đề `location_infrastructure` được thêm ngày 15/11/2026, lý do ở [docs/EVAL_RESULTS.md](docs/EVAL_RESULTS.md).

## Giới hạn cần biết

- **Che PII mới ở mức cơ bản.** Chỉ che email, số di động Việt Nam (đầu `0` hoặc `+84`) và tên khách hàng nếu file đầu vào có `customer_name`. Tên người chưa biết trước, số máy bàn, số CCCD, địa chỉ, tài khoản mạng xã hội **không** được che. Chưa nên đưa dữ liệu thật vào.
- **Bản nháp insight chưa qua duyệt.** Lệnh `summary --project` chỉ in dòng "BẢN NHÁP — CẦN QUẢN LÝ RÀ SOÁT"; chưa có trạng thái duyệt, người duyệt hay cơ chế chặn.
- **Chưa có dữ liệu thời gian** nên chưa thể kết luận vấn đề nào đang tăng.
- **Dữ liệu mẫu chỉ có 9 phản hồi tự viết.** Tỷ lệ đúng in ra khi chạy `analyze` không phản ánh chất lượng trên dữ liệu thật.

## Kiểm thử

```powershell
python -m pytest        # 37 test, không gọi mạng, không cần API key
python -m ruff check .
```

## Cấu trúc

```
src/
  __main__.py   CLI: analyze, summary, chat
  config.py     Cấu hình từ biến môi trường: model, timeout, retry, đường dẫn
  schemas.py    Schema dữ liệu; nguồn duy nhất cho topic, sentiment, source
  privacy.py    Che PII bằng regex
  prompts.py    System prompt của ba lời gọi LLM
  llm.py        Truy cập Gemini: tạo client, phân loại, viết insight, xử lý lỗi
  storage.py    Đọc phản hồi đầu vào, đọc/ghi báo cáo JSON
  pipeline.py   Che PII → phân loại → kiểm tra bằng chứng → so nhãn
  stats.py      Thống kê theo dự án, tính bằng code
  tools.py      Hai tool chỉ-đọc cho agent hội thoại
  agent.py      Vòng lặp gọi tool của agent hội thoại
tests/          Test đơn vị, dùng client giả thay cho Gemini
data/           Dữ liệu mẫu
docs/           Hiện trạng, kế hoạch sprint, checklist sprint hiện tại, kết quả đánh giá
```
