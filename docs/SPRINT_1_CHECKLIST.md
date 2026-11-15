# Checklist Sprint 1

**Mục tiêu sprint.** Trên khoảng 360 phản hồi tổng hợp có PII giả, quản lý hỏi được "DuAnB, tháng 9, kênh CRM: bao nhiêu phản hồi tiêu cực về tiến độ, trên tổng bao nhiêu, là những phản hồi nào" và nhận được con số kèm ID; đồng thời biết bao nhiêu PII đã lọt qua bước che.

**Khối lượng.** 16 điểm còn lại (Task 1–8). Đã xong ngoài kế hoạch 4 điểm: thu thập và gán nhãn 164 đánh giá thật (VOC-06), thêm chủ đề `location_infrastructure` (VOC-26). Bối cảnh và lý do của từng mục xem ở [SPRINT_PLAN.md](SPRINT_PLAN.md#sprint-1-số-liệu-có-thời-gian-truy-vết-được-đo-được-lọt-pii).

**Cách dùng.** Đánh dấu `[x]` khi xong. Commit sau mỗi task, đừng dồn đến cuối tuần. Mỗi ngày ghi ba dòng vào phần [Nhật ký](#nhật-ký-hằng-ngày) ở cuối file.

## Tiến độ (cập nhật 15/11/2026, hết ngày 1)

- **Task 1 gần xong:** đã commit và push lên nhánh `sprint1/refactor-va-du-lieu-that`; còn gộp vào `main`. **Task 2–9: chưa bắt đầu.** `pytest` 37 test pass, `ruff` sạch.
- **Đã xong ngoài kế hoạch:**
  - Thu thập 1.202 đánh giá Google Maps của 3 dự án, lọc và gán nhãn được 164 câu (công cụ ở `E:\VoC-data-collector`).
  - Đo lần đầu trên dữ liệu thật: chủ đề khớp 70,6%, cảm xúc khớp 92,0% (xem [EVAL_RESULTS.md](EVAL_RESULTS.md)).
  - Thêm chủ đề `location_infrastructure` vào schema và prompt (Q6). Đo lại: chủ đề khớp 79,8%, cảm xúc 92,6%.
- **Thay đổi phạm vi:** Task 8 đổi từ API (VOC-60, dời sang Sprint 3) thành giới hạn tốc độ gọi LLM (VOC-28), vì lượt đo ngày 15/11 có 35/164 lời gọi bị lỗi 429.
- **Quyết định:** Q1–Q7 đã chốt hết. Sprint 1 kết thúc muộn một ngày, giữ nguyên phạm vi (xác nhận 15/11).

## 0. Trước khi bắt đầu

- [ ] Kiểm tra hạn mức của `GEMINI_API_KEY` trên Google AI Studio: cần khoảng 400 lời gọi cho cả sprint.
- [ ] Chốt 5 quyết định dưới đây và ghi vào cột "Chốt".

| # | Câu hỏi | Đề xuất | Chốt |
| --- | --- | --- | --- |
| Q1 | Có theo dõi thư mục `outputs/` trong Git không? | Không. `.gitignore` đang bỏ qua vì báo cáo có nội dung phản hồi | Theo đề xuất (15/11) |
| Q2 | Báo cáo cũ chưa có `created_at` thì xử lý thế nào? | Để `created_at` là trường bắt buộc, rồi chạy lại `analyze` để tạo báo cáo mới (9 lời gọi) | Theo đề xuất (15/11) |
| Q3 | Lọc theo ngày dùng múi giờ nào? | Giờ Việt Nam, cố định UTC+7 (`timezone(timedelta(hours=7))`). Việt Nam không đổi giờ theo mùa nên cách này chính xác. **Không** dùng `ZoneInfo("Asia/Ho_Chi_Minh")`: trên máy này lệnh đó lỗi `ZoneInfoNotFoundError` vì chưa cài `tzdata` (đã thử) | Theo đề xuất (15/11) |
| Q4 | Che mọi dãy 12 chữ số như CCCD, hay chỉ khi có từ khóa? | Chỉ khi có từ khóa "CCCD", "CMND" hoặc "căn cước" đứng trước, để không che nhầm số tiền | Theo đề xuất (15/11) |
| Q5 | Thông số bộ dữ liệu tổng hợp? | 360 phản hồi (15 mỗi dự án mỗi tuần); 3 dự án (DuAnA, DuAnB, DuAnC); 4 nguồn; 8 tuần từ thứ Hai 03/08/2026 đến Chủ nhật 27/09/2026; điểm nóng ở DuAnB, chủ đề `construction_progress`, 2 tuần cuối; dự án đối chứng DuAnC chê giá nhiều nhưng ổn định; khoảng 25% bản ghi có PII giả | Theo đề xuất (15/11) |
| Q6 | Dữ liệu group cư dân Facebook có nhiều phản hồi ngoài 6 chủ đề. Có mở rộng danh sách chủ đề không? | Đọc lướt khoảng 50 bài và đếm trước khi quyết định | Không mở rộng (15/11). Loại group cư dân vì phần lớn bài là chuyện đời sống, rao vặt, không phải phản hồi về dự án. Xem lại nếu nguồn mới cho nhiều nhãn `other`. **Cần xem lại (15/11):** trên 164 đánh giá Google Maps có 45 câu (28%) là `other`, lớn nhất là vị trí/giao thông (14) và quy hoạch/kiến trúc (9); model xếp 33 câu trong số đó vào `amenities`. Chi tiết ở [EVAL_RESULTS.md](EVAL_RESULTS.md). **Đã chốt phương án A (15/11):** thêm chủ đề `location_infrastructure` (vị trí, giao thông, hạ tầng kỹ thuật); quy hoạch, kiến trúc, vệ sinh, an ninh vẫn là `other` |
| Q7 | Có dùng dữ liệu thật trong Sprint 1 không, lấy từ đâu? | Thử 3 nguồn, mỗi nguồn 30–45 phút: bình luận fanpage dự án, bình luận báo điện tử về dự án cụ thể, đánh giá Google Maps. Sau khoảng 2 giờ mà chưa được 50 phản hồi dùng được thì Sprint 1 chỉ dùng bộ tổng hợp; dữ liệu thật để sang VOC-70 (Sprint 2) | Xong (15/11): Google Maps, thu bằng `E:\VoC-data-collector` (Chrome đã đăng nhập). 1.202 đánh giá thô → 164 câu có nhãn (Claude gán, người dùng chấp nhận). Kết quả đo đầu tiên ở [EVAL_RESULTS.md](EVAL_RESULTS.md) |

## Task 1. VOC-84: Dọn repo và commit phần refactor (1 điểm)

- [ ] Xem lại toàn bộ thay đổi bằng `git status` và `git diff`, chú ý `src/`, `tests/`, `docs/`.
- [x] Mở file `er.name Ten cua ban`, xác nhận là rác rồi xóa.
- [x] Chạy `git check-ignore .env outputs/analysis_report.json`. Lệnh phải in ra cả hai đường dẫn, nghĩa là cả hai đều bị Git bỏ qua.
- [x] Chạy `python -m pytest` (kỳ vọng 37 passed) và `python -m ruff check .` (kỳ vọng sạch).
- [x] Chạy `git add -A` rồi `git status`. Danh sách staged không được có `.env`, `outputs/`, `.venv/` hay `__pycache__/`.
- [x] Commit rồi `git push`. Đã push 2 commit lên nhánh `sprint1/refactor-va-du-lieu-that` ngày 15/11.
- [ ] Gộp nhánh đó vào `main` (tạo pull request trên GitHub rồi merge).

**Xong khi:** `git status` sạch và push thành công.

## Task 2. VOC-01: Thêm thời gian và kênh tổng đài (2 điểm)

Phụ thuộc: Task 1, Q2, Q3.

**Code**

- [ ] [src/schemas.py](../src/schemas.py): thêm `"call_center"` vào `Source`.
- [ ] [src/schemas.py](../src/schemas.py): thêm trường `created_at: AwareDatetime` vào `Feedback` (kiểu này từ chối thời gian không có múi giờ). Thêm `field_validator` đổi giá trị về UTC bằng `value.astimezone(timezone.utc)`, vì `AwareDatetime` giữ nguyên `+07:00` chứ không tự đổi.
- [ ] [src/schemas.py](../src/schemas.py): thêm `created_at` vào `AnalyzedFeedback`.
- [ ] [src/pipeline.py](../src/pipeline.py): truyền `created_at=feedback.created_at` khi tạo `AnalyzedFeedback`.
- [ ] [src/storage.py](../src/storage.py), hàm `save_report`: đổi `report.model_dump()` thành `report.model_dump(mode="json")`. **Bắt buộc**, vì `json.dump` không ghi được `datetime` (đã thử: `TypeError`).
- [ ] [data/mock_feedback.json](../data/mock_feedback.json): thêm `created_at` cho 9 bản ghi, dạng `"2026-09-01T09:00:00+07:00"`. File dữ liệu thật `real_feedback.json` đã có sẵn trường này (ngày ước tính).

**Test**

- [ ] [tests/conftest.py](../tests/conftest.py): thêm `created_at` vào `_record` và `SAMPLE_REPORT`.
- [ ] [tests/test_pipeline.py](../tests/test_pipeline.py), [tests/test_storage.py](../tests/test_storage.py): thêm `created_at` vào những chỗ đang dựng `Feedback`.
- [ ] Viết test mới cho các ca sau:
  - Thiếu `created_at` thì bản ghi bị loại, kèm `id`.
  - Thời gian không có múi giờ thì bản ghi bị loại.
  - `09:00+07:00` được lưu thành `02:00Z`.
  - `source="call_center"` hợp lệ.
  - Ghi báo cáo rồi đọc lại vẫn giữ đúng `created_at`.

**Kiểm tra**

- [ ] `pytest` và `ruff` pass.
- [ ] Chạy `python -m src analyze` (9 lời gọi thật) để tạo lại báo cáo. Sau đó `summary` và `chat` phải đọc được báo cáo mới. Báo cáo cũ sẽ bị từ chối với thông báo `results.0.created_at: Field required`; đó là hành vi đúng.
- [ ] [README.md](../README.md): thêm `created_at` và `call_center` vào bảng trường đầu vào.
- [ ] Commit.

## Task 3. VOC-02: Bộ dữ liệu tổng hợp (3 điểm)

Phụ thuộc: Task 2, Q5.

- [ ] Tạo `scripts/generate_synthetic.py` với các tham số `--seed` (mặc định 42), `--count` (mặc định 360), `--out-dir` (mặc định `data/`).
- [ ] Bảo đảm cùng seed luôn cho ra cùng file:
  - Dùng một đối tượng `random.Random(seed)` riêng.
  - Ngày bắt đầu cố định, không dùng `datetime.now()`.
  - Duyệt danh sách theo thứ tự cố định.
- [ ] Mẫu câu: mỗi cặp (chủ đề, cảm xúc) có ít nhất 3 mẫu (7 × 3 = 21 cặp, tức khoảng 63 câu), có chỗ trống để thay từ nên câu không trùng hệt. Lấy `expected_topic` và `expected_sentiment` theo mẫu câu.
- [ ] Bảo đảm đủ mẫu cho các lớp mà dữ liệu thật thiếu: `legal_process` (0 câu thật), `construction_progress` (6), `neutral` (2). Bộ tổng hợp hiện là nguồn duy nhất cho các lớp này.
- [ ] Văn phong theo kênh. Khảo sát: ngôi thứ nhất. CRM: ghi chú của sale, ví dụ "KH phản ánh ...". Mạng xã hội: giọng thân mật, khoảng 10% viết không dấu. Tổng đài: dạng tóm tắt cuộc gọi, ví dụ "Khách gọi lên phản ánh: ...".
- [ ] Phân bổ: mỗi dự án mỗi tuần 15 phản hồi (3 × 8 × 15 = 360). Nguồn chọn ngẫu nhiên theo tỷ lệ CRM 30%, khảo sát 25%, mạng xã hội 30%, tổng đài 15%. Ngày và giờ chọn ngẫu nhiên trong tuần, ghi kèm `+07:00`.
- [ ] Cài điểm nóng: ở DuAnB, tỷ lệ phản hồi `construction_progress` tiêu cực trong 2 tuần cuối phải cao rõ so với 6 tuần trước, ví dụ từ khoảng 10% lên khoảng 35% số phản hồi của DuAnB mỗi tuần.
- [ ] Cài dự án đối chứng: ở DuAnC, tỷ lệ `price` tiêu cực ở mức khoảng 30% và giữ ổn định suốt 8 tuần. Số lượng ở mức cao nhưng không tăng, nên Sprint 2 **không** được báo DuAnC là điểm nóng.
- [ ] Chèn PII giả vào khoảng 25% bản ghi, đủ 6 loại:
  - email `@example.com`
  - số di động, trộn nhiều cách viết: `0912 345 678`, `0912.345.678`, `+84 912 345 678`, `84912345678`, `(+84) 912 345 678`
  - số máy bàn
  - CCCD có từ khóa
  - link mạng xã hội
  - họ tên ghép từ danh sách họ và tên phổ biến

  Không dùng thông tin của người thật.
- [ ] Với một nửa số bản ghi có tên, điền thêm trường `customer_name`. Ghi loại tên trong bảng kê là `name_declared` hoặc `name_undeclared`, để đo riêng hai trường hợp.
- [ ] Ghi ra `data/synthetic_feedback.json` và `data/synthetic_pii_manifest.json`. Bảng kê có dạng `{"<id>": [{"type": "phone", "value": "..."}]}`, và mỗi `value` phải đúng nguyên văn chuỗi đã chèn vào `text`.
- [ ] Script in bảng tóm tắt: số phản hồi theo dự án, nguồn, tuần, chủ đề, và số PII theo loại.

**Kiểm tra**

- [ ] Chạy script 2 lần với cùng seed. `Get-FileHash data\synthetic_*.json` phải cho cùng giá trị băm ở cả hai lần.
- [ ] `load_feedbacks` trên file sinh ra không loại bản ghi nào.
- [ ] Đọc tay 10 bản ghi ngẫu nhiên: câu phải tự nhiên và nhãn đúng.
- [ ] Viết `tests/test_synthetic.py` kiểm tra hai điều: cùng seed cho cùng output; mọi `value` trong bảng kê đều nằm trong `text` của đúng `id`.
- [ ] [README.md](../README.md): thêm mục "Dữ liệu tổng hợp", mô tả lệnh chạy và phân phối dữ liệu.
- [ ] Commit.

## Task 4. VOC-10: Mở rộng che PII (2 điểm)

Phụ thuộc: Q4. Không phụ thuộc Task 3 nên có thể làm xen kẽ.

- [ ] Viết test trước trong [tests/test_privacy.py](../tests/test_privacy.py) cho 5 ca đang lọt (xem [PROJECT_STATUS.md mục 5.1](PROJECT_STATUS.md#51-privacy)): `84901234567`, `(+84) 901 234 567`, `02438123456`, `CCCD 001099012345`, `fb.com/nguyenvanan.1990`. Chạy để thấy các test này fail.
- [ ] Thêm ca chống che nhầm:
  - `Giá 3.200.000.000 đồng`
  - `ngày 01/02/2026`
  - `Hợp đồng số 12345`
  - `căn B12.05`
  - `diện tích 75,5 m2`
  - `mã căn A0901234567B`
  - dãy 12 chữ số không có từ khóa (nếu Q4 chốt theo đề xuất)
- [ ] [src/privacy.py](../src/privacy.py): thêm các mẫu regex và nhãn thay thế mới (`[ID_NUMBER]`, `[SOCIAL]`). Có thể gộp dạng `84...` và `(+84)` vào `PHONE_PATTERN`.
- [ ] Sắp thứ tự thay thế để mẫu cụ thể chạy trước, tránh trường hợp `[PHONE]` thay mất một phần số CCCD.
- [ ] Cập nhật docstring đầu file [src/privacy.py](../src/privacy.py) để nêu đúng phạm vi che mới.

**Kiểm tra**

- [ ] Các test cũ trong `test_privacy.py` vẫn pass, không sửa kỳ vọng cũ.
- [ ] Mục "Giới hạn cần biết" trong [README.md](../README.md) được cập nhật.
- [ ] Commit.

## Task 5. VOC-13: Lệnh `pii-check` (2 điểm)

Phụ thuộc: Task 3, Task 4.

- [ ] Tạo `src/pii_check.py` với hàm thuần `check_leaks(report, manifest)`. Hàm trả về theo từng loại PII: số mục được kiểm, số mục lọt, tỷ lệ lọt và danh sách `id` bị lọt.
- [ ] Mẫu số chỉ gồm PII của những `id` có trong `report.results`. Bản ghi phân tích lỗi không có văn bản trong báo cáo, nếu tính vào sẽ làm tỷ lệ lọt thấp giả.
- [ ] Một mục bị tính là "lọt" khi giá trị trong bảng kê còn xuất hiện trong `text` hoặc `evidence` của bản ghi.
- [ ] Thêm lệnh CLI `python -m src pii-check --report ... --manifest ...`. Lệnh chỉ in `id` và loại, **không in giá trị PII**.
- [ ] (Tùy chọn) Thêm tham số `--input <file phản hồi>` để che PII rồi đo ngay, không gọi LLM. Kết quả giống hệt đo trên báo cáo, vì LLM nhận đúng văn bản đã che đó, nên dùng được để thử nhanh sau mỗi lần sửa regex.
- [ ] Test với báo cáo và bảng kê giả, gồm 3 ca: một mục lọt, một mục không lọt, một `id` phân tích lỗi bị loại khỏi mẫu số.
- [ ] Tạo `docs/EVAL_RESULTS.md` với khung bảng gồm: ngày, model, mã băm prompt, bộ dữ liệu và seed, chỉ số, ghi chú.
- [ ] Thêm lệnh mới vào [README.md](../README.md), rồi commit.

## Task 6. VOC-20: Ghi nhận token và thông tin lượt chạy (2 điểm)

Phụ thuộc: Task 2. Phải xong trước Task 9.

- [ ] [src/llm.py](../src/llm.py): thêm dataclass `TokenUsage` gồm `input`, `output`, `thoughts`, `calls`.
- [ ] Sửa `classify_feedback` nhận thêm tham số `usage=None` và cộng `response.usage_metadata` vào đó. Chú ý ba điểm:
  - Đọc bằng `getattr(response, "usage_metadata", None)`, vì response giả trong test không có trường này.
  - Giá trị `None` tính là 0. Thực tế `thoughts_token_count` trả về `None`.
  - Cộng ngay khi nhận response, trước bước kiểm schema, vì lời gọi trả sai schema vẫn tốn token.
- [ ] [src/schemas.py](../src/schemas.py): thêm model `RunMeta` gồm `run_id`, `started_at`, `finished_at`, `duration_seconds`, `model`, `prompt_sha256`, `input_count`, `success_count`, `error_count`, các trường token và `llm_calls`. Thêm `AnalysisReport.meta: RunMeta | None = None`.
- [ ] Thêm hàm tính mã băm prompt: SHA-256 của `CLASSIFY_INSTRUCTIONS`, lấy 12 ký tự đầu.
- [ ] [src/\_\_main\_\_.py](../src/__main__.py), hàm `cmd_analyze`: tạo `TokenUsage`, đo thời gian, gắn `meta` vào báo cáo và in tổng token.
- [ ] Test: client giả trả `usage_metadata` khác nhau qua 3 lời gọi, trong đó 1 lời gọi lỗi schema; tổng token phải khớp. Thêm test xác nhận báo cáo không có `meta` vẫn đọc được bằng `load_report`.
- [ ] Ghi chú giới hạn trong docstring: token của những lần SDK tự thử lại mà thất bại thì không đếm được.
- [ ] Commit.

## Task 7. VOC-30: Thống kê có bộ lọc và kèm ID (3 điểm)

Phụ thuộc: Task 2, Q3.

- [ ] [src/stats.py](../src/stats.py): thêm hàm `compute_stats(records, project=None, source=None, date_from=None, date_to=None)`. Hàm trả về phạm vi lọc, mẫu số và danh sách ô; mỗi ô gồm `topic`, `sentiment`, `count`, `rate_percent`, `ids`.
- [ ] Quy tắc lọc ngày:
  - Đổi `created_at` (UTC) sang giờ Việt Nam rồi lấy `.date()`.
  - Tính cả ngày đầu và ngày cuối của khoảng.
- [ ] Mẫu số là số phản hồi phân tích thành công trong phạm vi. Khi mẫu số bằng 0 thì không thực hiện phép chia.
- [ ] Giữ nguyên `summarize_projects` và `stats_payload` để lệnh `summary` và tool hiện tại không đổi hành vi. Việc gộp hai đường tính để lại sau.
- [ ] Thêm lệnh `python -m src stats --project DuAnB --source crm --from 2026-09-01 --to 2026-09-30 [--show-ids]`. Ngày sai định dạng thì báo lỗi rõ ràng.
- [ ] Tool `get_project_stats`: thêm `date_from` và `date_to` tùy chọn, định dạng `YYYY-MM-DD`; sai định dạng thì trả `status: invalid_input`. Cập nhật `TOOL_DEFINITIONS` trong [src/agent.py](../src/agent.py) tương ứng.

**Test bất biến**

- [ ] Tổng `count` của các ô bằng mẫu số.
- [ ] Hợp các `ids` bằng đúng tập `id` sau lọc, và không ô nào trùng `id` với ô khác.
- [ ] Phạm vi rỗng cho mẫu số 0 và không gây lỗi.
- [ ] Ca biên múi giờ: phản hồi lúc `2026-09-30T23:30+07:00` (tức `16:30Z`) thuộc ngày 30/9, không thuộc ngày 1/10.
- [ ] Các test cũ trong [tests/test_stats_tools.py](../tests/test_stats_tools.py) vẫn pass mà không phải sửa.
- [ ] Cập nhật [README.md](../README.md), rồi commit.

## Task 8. VOC-28: Giới hạn tốc độ gọi LLM (1 điểm)

Không phụ thuộc task nào; phải xong trước Task 9. Thay cho VOC-60 (API chỉ-đọc), đã dời sang Sprint 3.

- [ ] [src/config.py](../src/config.py): thêm `requests_per_minute` vào `Settings`, đọc từ `VOC_REQUESTS_PER_MINUTE`, mặc định 15 (giới hạn của gói Gemini miễn phí). Thêm dòng tương ứng vào [.env.example](../.env.example).
- [ ] [src/llm.py](../src/llm.py): trong `generate`, chờ cho đủ khoảng cách tối thiểu `60 / requests_per_minute` giây kể từ lời gọi trước. Cho phép truyền đồng hồ và hàm chờ từ ngoài vào để test không phải chờ thật.
- [ ] Test với đồng hồ giả: 3 lời gọi liên tiếp thì tổng thời gian chờ là 2 khoảng; hai lời gọi cách xa nhau thì không chờ.
- [ ] Cập nhật `tests/conftest.py` để `Settings` trong test có trường mới.
- [ ] Chạy lại 164 câu thật với retry mặc định (không đặt `VOC_RETRY_ATTEMPTS`): không còn lỗi 429.
- [ ] Ghi vào [README.md](../README.md): với 15 lời gọi/phút, 360 phản hồi mất khoảng 24 phút. Commit.

## Task 9. Chạy thật, ghi số đo, chuẩn bị demo

Phụ thuộc: Task 3 đến 8.

- [ ] `python scripts/generate_synthetic.py --seed 42`
- [ ] `python -m src analyze --input data\synthetic_feedback.json --output outputs\synthetic_report.json`. Với giới hạn 15 lời gọi/phút (Task 8), 360 lời gọi mất khoảng 24 phút. Nếu vẫn gặp lỗi 429, sinh bộ nhỏ hơn bằng `--count 120` và ghi rõ điều đó trong kết quả.
- [ ] `python -m src pii-check --report outputs\synthetic_report.json --manifest data\synthetic_pii_manifest.json`
- [ ] Chọn 5 con số bất kỳ từ lệnh `stats`, đếm lại trực tiếp trong file báo cáo theo `id`; cả 5 phải khớp.
- [ ] Điền [docs/EVAL_RESULTS.md](EVAL_RESULTS.md) các mục sau:
  - ngày chạy, model, mã băm prompt
  - seed và số bản ghi
  - thời gian chạy, tổng token, số bản ghi lỗi
  - tỷ lệ khớp nhãn, ghi rõ đây là cận trên vì câu sinh từ mẫu dễ phân loại hơn câu thật
  - tỷ lệ lọt PII theo loại
- [ ] Chạy thử kịch bản demo ở mục dưới một lượt từ đầu đến cuối.

## Kết thúc sprint

**Tiêu chí nghiệm thu** (đánh dấu trong buổi Review)

- [ ] Bộ dữ liệu tổng hợp đã được phân tích xong và tỷ lệ bản ghi lỗi được ghi lại.
- [ ] Lệnh `stats` lọc được theo dự án, nguồn, thời gian và trả về `id`; test bất biến pass.
- [ ] Tỷ lệ lọt PII theo từng loại được ghi lại. Kỳ vọng: email và số điện thoại không lọt, `name_undeclared` vẫn lọt (sẽ xử lý ở VOC-11).
- [ ] Tổng token của lượt chạy được ghi lại.

**Kịch bản demo**

1. Sinh dữ liệu tổng hợp.
2. Chạy `analyze`, xem phần tổng kết và số token.
3. Chạy `pii-check`, đọc tỷ lệ lọt theo từng loại.
4. Chạy `stats` cho DuAnB ở tháng 8 và tháng 9, chỉ ra mẫu số, mở 2 `id` bất kỳ để đối chiếu với văn bản gốc đã che.

**Cập nhật tài liệu, Review và Retro**

- [ ] [PROJECT_STATUS.md](PROJECT_STATUS.md): cập nhật các dòng 2 (chuẩn hóa), 13 (PII), 15 (số liệu), 16 (chi phí), 18 (kiểm thử) trong bảng đối chiếu.
- [ ] [SPRINT_PLAN.md](SPRINT_PLAN.md): ghi số điểm thực tế đã hoàn thành. Chỉ tính task đạt đủ tiêu chí, không tính điểm một phần. Con số này dùng để xếp Sprint 2.
- [ ] Review 30 phút: chạy kịch bản demo và đánh dấu tiêu chí nghiệm thu.
- [ ] Retro 15 phút: ghi một điều nên giữ, một điều nên đổi, một điều muốn thử.

**Mỗi task được tính là xong khi:**

- `pytest` và `ruff` pass.
- Fixture và log không chứa PII thật hay secret.
- Con số hiển thị cho người dùng do code tính và có mẫu số.
- README đã cập nhật nếu lệnh chạy hoặc hành vi thay đổi.

## Gợi ý lịch cho phần còn lại

Ngày 1 đã dùng cho việc ngoài kế hoạch, nên 16 điểm còn lại cần khoảng 5 ngày làm việc nữa. Sprint 1 vì vậy kết thúc muộn hơn dự kiến một ngày, giữ nguyên phạm vi (đã xác nhận 15/11).

| Ngày | Task |
| --- | --- |
| 1 (15/11) | Đã làm: thu thập và gán nhãn dữ liệu thật, đo lần đầu, thêm chủ đề mới |
| 2 | Task 1, Task 2 |
| 3 | Task 3 |
| 4 | Task 4, Task 5, Task 8 |
| 5 | Task 6, Task 7 |
| 6 | Task 9, cập nhật tài liệu, Review và Retro |

## Nhật ký hằng ngày

| Ngày | Đã xong | Làm tiếp | Vướng |
| --- | --- | --- | --- |
| 15/11 | Chốt Q1–Q4, Q6, Q7. Thu thập 1.202 đánh giá Google Maps, gán nhãn 164 câu. Đo lần đầu trên dữ liệu thật. Thêm chủ đề `location_infrastructure` | Task 1 (commit), Task 2 | Gói Gemini miễn phí giới hạn 15 lời gọi/phút |
| | | | |
