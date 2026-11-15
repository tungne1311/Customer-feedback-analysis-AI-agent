# Hiện trạng dự án VoiceOfCustomer

Ngày khảo sát: 2026-11-10. Căn cứ: đọc toàn bộ code, chạy test và chạy thật với Gemini trên dữ liệu mẫu. Tài liệu mô tả code **sau refactor**.

> **Thay đổi sau ngày khảo sát (cập nhật 15/11/2026):** đã có 164 đánh giá Google Maps thật có nhãn, hai lượt đo đầu tiên, và chủ đề thứ bảy `location_infrastructure`. Số đo ở [EVAL_RESULTS.md](EVAL_RESULTS.md); tiến độ mới nhất ở [SPRINT_PLAN.md](SPRINT_PLAN.md#4-kế-hoạch-sprint). Các phần còn lại của tài liệu này vẫn đúng.

## 1. Tóm tắt

Repo là một công cụ dòng lệnh Python (1.165 dòng sau refactor, chưa tính test; lịch sử Git có một commit) làm được ba việc trên file dữ liệu mẫu 9 phản hồi:

1. Phân loại chủ đề và cảm xúc từng phản hồi bằng Gemini, kèm đoạn trích bằng chứng.
2. Thống kê tỷ lệ tiêu cực theo dự án bằng code và nhờ Gemini viết bản nháp insight từ các con số đó.
3. Hỏi đáp qua một agent gọi tool để lấy thống kê và phản hồi cụ thể.

Cả ba đã chạy thật end-to-end với Gemini trong lần khảo sát này. Phần còn lại của đề bài chưa có code: thu thập từ kênh thật, dữ liệu thời gian, embedding/gom cụm, phát hiện điểm nóng, LangGraph, vector database, FastAPI, dashboard Next.js, quy trình duyệt và triển khai.

Không ước lượng phần trăm hoàn thành vì chưa có cách tính đáng tin cậy; bảng đối chiếu ở mục 4 liệt kê từng yêu cầu.

## 2. Luồng dữ liệu đang chạy

```
data/mock_feedback.json
        │  storage.load_feedbacks      kiểm tra schema, loại bản ghi sai hoặc trùng id
        ▼
pipeline.analyze_feedbacks  (với từng phản hồi)
        │  privacy.redact_pii          che email, số di động, tên đã biết
        │  llm.classify_feedback       Gemini → {topic, sentiment, evidence}
        │  pipeline.check_evidence     evidence phải là đoạn trích có trong văn bản
        │  so với nhãn đúng nếu có
        ▼
outputs/analysis_report.json           {results, errors}
        │
        ├─► stats.summarize_projects ─► in thống kê ─► llm.generate_insight ─► bản nháp in ra màn hình
        │        (lệnh summary)                         (chỉ khi có --project)
        │
        └─► tools.get_project_stats / get_negative_feedback ◄─ agent.run_agent ◄─ lệnh chat
```

Ba lệnh chạy độc lập và nối với nhau qua file báo cáo JSON. Không có cơ sở dữ liệu, không có dịch vụ nền, không có bộ điều phối.

**Luồng theo đề bài (chưa có):** Ingest đa kênh → Redact → Cluster (embedding) → Analyze → Hotspot → Summarize → Propose → Duyệt (HITL) → Dashboard. Kế hoạch xây dựng ở [SPRINT_PLAN.md](SPRINT_PLAN.md).

### Phần nào dùng LLM, phần nào là code

| Bước | Thực hiện bởi |
| --- | --- |
| Kiểm tra schema, loại trùng, che PII | Code (pydantic, regex) |
| Chọn chủ đề, cảm xúc, trích bằng chứng | LLM, một lời gọi cho mỗi phản hồi, output ép theo JSON schema |
| Kiểm tra bằng chứng có trong văn bản | Code |
| Đếm, tính tỷ lệ | Code |
| Viết tóm tắt và đề xuất | LLM, đầu vào chỉ là các con số đã tính |
| Quyết định gọi tool nào khi hỏi đáp | LLM (function calling); tool là code chỉ-đọc |

## 3. Bản đồ module

| Module | Trách nhiệm | Input → Output | Được gọi từ | Trạng thái | Vấn đề còn lại |
| --- | --- | --- | --- | --- | --- |
| [src/\_\_main\_\_.py](../src/__main__.py) | CLI ba lệnh `analyze`, `summary`, `chat`; in kết quả; đổi lỗi thành mã thoát | Tham số dòng lệnh → màn hình, file báo cáo | Người dùng | Chạy thật được cả ba lệnh | Là giao diện duy nhất; chưa có API |
| [src/config.py](../src/config.py) | Đọc cấu hình từ biến môi trường và `.env` | Env → `Settings` | `__main__`, `tools` | Có test gián tiếp | Ba biến model cùng mặc định một model |
| [src/schemas.py](../src/schemas.py) | Schema `Feedback`, `FeedbackAnalysis`, `AnalyzedFeedback`, `AnalysisReport`; danh sách topic/sentiment/source | — | Mọi module | Có test | Chưa có timestamp; `source` chưa có kênh tổng đài |
| [src/privacy.py](../src/privacy.py) | Che PII bằng regex | Chuỗi → chuỗi đã che | `pipeline` | Có test | Bao phủ hẹp, xem mục 5.1 |
| [src/prompts.py](../src/prompts.py) | Ba system prompt | — | `llm`, `agent` | Giữ nguyên văn từ code gốc | Chưa có phiên bản prompt; chưa có tập đánh giá để kiểm khi sửa |
| [src/llm.py](../src/llm.py) | Tạo client Gemini (timeout, retry); phân loại; viết insight; gom lỗi thành `LLMError` | Văn bản đã che → `FeedbackAnalysis`; số liệu → văn bản | `pipeline` (qua `__main__`), `agent` | Có test với client giả; đã chạy thật | Chưa ghi nhận token/chi phí; gọi tuần tự |
| [src/storage.py](../src/storage.py) | Đọc phản hồi, đọc/ghi báo cáo JSON | File ↔ model | `__main__`, `tools` | Có test | Lưu bằng một file JSON, mỗi lần chạy ghi đè |
| [src/pipeline.py](../src/pipeline.py) | Điều phối phân tích từng phản hồi; so nhãn | `Feedback[]` → `AnalysisReport` | `__main__` | Có test; đã chạy thật | Vòng lặp tuần tự; lỗi ở bản ghi nào thì bỏ bản ghi đó, không thử lại ở tầng này |
| [src/stats.py](../src/stats.py) | Đếm theo dự án: tổng, tiêu cực, tiêu cực theo chủ đề | `AnalyzedFeedback[]` → `ProjectStats` | `__main__`, `tools` | Có test | Chưa chia theo nguồn, thời gian; chưa trả danh sách ID |
| [src/tools.py](../src/tools.py) | Hai tool chỉ-đọc cho agent | Tham số → dict có `status` | `agent` | Có test; đã chạy thật | Đọc lại file ở mỗi lần gọi |
| [src/agent.py](../src/agent.py) | Vòng lặp function calling, giới hạn số bước, chặn tool lạ | Lịch sử hội thoại → câu trả lời | `__main__` | Có test với client giả; đã chạy thật | Một agent duy nhất; câu trả lời không qua duyệt |
| [data/mock_feedback.json](../data/mock_feedback.json) | Dữ liệu mẫu có nhãn | — | `analyze` | 9 phản hồi tự viết, 2 dự án, 3 nguồn | Không có thời gian, không có PII, quá ít để đánh giá |

Không có phụ thuộc vòng. Chiều phụ thuộc: `__main__` → `agent`/`pipeline` → `llm`/`tools`/`stats`/`storage`/`privacy` → `schemas`/`config`/`prompts`.

### Vấn đề phát hiện ở code gốc

| Phát hiện | Loại | Xử lý |
| --- | --- | --- |
| `privacy.redact_pii` không được gọi ở đâu; văn bản gốc đi thẳng tới Gemini và file báo cáo | Code chết, thiếu guardrail | Đã nối vào pipeline |
| Danh sách chủ đề khai báo ở 3 file, tên model ở 3 file, đường dẫn và đoạn đọc báo cáo ở 4 chỗ | Trùng lặp, hard-code | Đã gom về `schemas`, `config`, `storage` |
| `main.py` làm 5 việc (đọc file, gọi LLM, kiểm tra, chấm điểm theo nhãn, ghi file) và bắt buộc mọi bản ghi có nhãn đúng | Một file quá nhiều việc; không chạy được trên dữ liệu không nhãn | Đã tách; nhãn thành tùy chọn |
| `project_summary.py` trộn hàm thống kê thuần với CLI và lời gọi LLM; `tools.py` import nó nên kéo theo cả SDK Gemini | Trách nhiệm lẫn lộn | Đã tách `stats` riêng |
| `project = "DuAnA"` viết cứng trong `project_summary.main` | Hard-code | Đã thành tham số `--project` |
| Không timeout (SDK mặc định chờ vô hạn), không retry; lỗi mạng làm dừng cả lượt và mất mọi kết quả vì báo cáo chỉ ghi ở cuối | Dễ phát sinh lỗi | Đã thêm timeout, retry có giới hạn, bắt lỗi theo từng bản ghi |
| Thông báo lỗi schema ghi vào báo cáo có kèm nguyên output của model | Rò dữ liệu qua lỗi | Đã bỏ giá trị đầu vào khỏi thông báo |
| In nguyên nội dung phản hồi và kết quả tool ra màn hình | Rò dữ liệu qua log | Mặc định chỉ in id và nhãn |
| Tỷ lệ tiêu cực làm tròn 1 chữ số ở chỗ này, 2 chữ số ở chỗ khác | Không nhất quán | Thống nhất 2 chữ số |
| Thiếu API key hoặc báo cáo sai cấu trúc → traceback `KeyError` | Xử lý lỗi | Đã có thông báo rõ và mã thoát |
| `.gitignore` có dòng `outputs/t` (gõ thiếu) nên `outputs/` không được bỏ qua | Cấu hình | Đã sửa |
| Không có README, test, `.env.example`; dependencies không ghim phiên bản | Thiếu hạ tầng dự án | Đã bổ sung |
| File lạ `er.name Ten cua ban` ở thư mục gốc (kết quả của một lệnh git gõ nhầm, chưa được Git theo dõi) | Rác | **Chưa xóa**, để bạn quyết định |

## 4. Đối chiếu với đề bài

Cột "Triển khai" nói code có hay chưa; cột "Xác minh" nói đã kiểm chứng bằng cách nào. Ưu tiên: **P0** cần cho MVP, **P1** yêu cầu nâng cao, **P2** hoàn thiện vận hành.

| # | Yêu cầu | Triển khai | Bằng chứng | Xác minh | Còn thiếu | Ưu tiên |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Thu thập đa kênh | **Chỉ có mock/demo** | Một file JSON, trường `source` nhận `crm`/`survey`/`social` | Đọc code và dữ liệu | Bộ nạp cho từng kênh; kênh tổng đài; nạp tăng dần | P0 (nạp file), P1 (kết nối thật) |
| 2 | Chuẩn hóa dữ liệu | **Có một phần** | `schemas.Feedback`, `storage.load_feedbacks` | Test `test_storage.py` | Timestamp; ánh xạ cột của từng kênh; loại trùng theo nội dung | P0 |
| 3 | Phân loại chủ đề | **Đã kiểm chứng** trên dữ liệu mẫu | `llm.classify_feedback`, chủ đề cố định (6 lúc khảo sát; thêm `location_infrastructure` ngày 15/11/2026) | Chạy thật 9/9 khớp nhãn; test với client giả | Tập đánh giá đủ lớn; phản hồi nhiều khía cạnh (hiện chỉ một chủ đề chính) | P0 (đánh giá), P2 (đa nhãn) |
| 4 | Phân tích cảm xúc | **Đã kiểm chứng** trên dữ liệu mẫu | Cùng lời gọi với chủ đề | Chạy thật 9/9 khớp nhãn | Như trên | P0 |
| 5 | Embedding, gom cụm | **Chưa có** | Không có code hay dependency | Tìm trong repo | Toàn bộ | P1 |
| 6 | Phát hiện điểm nóng | **Chưa có** | Dữ liệu không có thời gian; prompt insight cấm kết luận "gia tăng" | Đọc code | Timestamp, đường cơ sở, phép so sánh, xử lý mẫu ít | P0 |
| 7 | Tổng hợp insight | **Có một phần** | `llm.generate_insight` | Chạy thật cho DuAnA | Chỉ nhận số đếm của một dự án, không đọc nội dung phản hồi hay cụm; output là văn bản tự do, không lưu | P0 |
| 8 | Đề xuất hành động | **Có một phần** | Cùng lời gọi, tối đa 2 đề xuất | Chạy thật | Cảnh báo rủi ro truyền thông; mức ưu tiên; liên kết đề xuất với số liệu nguồn | P0 |
| 9 | LangGraph, multi-agent | **Chưa có** | Không có `langgraph`; luồng là các hàm Python gọi nối tiếp và một agent gọi tool | Đọc code, `pip list` | Đồ thị, state có kiểu, các agent chuyên trách | P0 (đồ thị), P1 (agent gom cụm) |
| 10 | Vector database | **Chưa có** | — | Tìm trong repo | Toàn bộ | P1 |
| 11 | FastAPI | **Chưa có** | Chỉ có CLI | Tìm trong repo | Toàn bộ | P0 |
| 12 | Next.js, drill-down | **Chưa có** | — | Tìm trong repo | Toàn bộ | P0 |
| 13 | Che PII | **Có một phần** | `privacy.redact_pii`, gọi trong `pipeline.analyze_feedbacks` trước LLM và trước khi ghi | Test `test_pipeline.py::test_pii_is_redacted_before_llm_and_in_report`; thử 9 ca biên | Tên người, số máy bàn, CCCD, địa chỉ, tài khoản MXH; đo tỷ lệ lọt | P0 |
| 14 | HITL | **Chỉ có mock/demo** | Một dòng in "BẢN NHÁP — CẦN QUẢN LÝ RÀ SOÁT" trong `__main__.cmd_summary` | Đọc code | Trạng thái duyệt, người duyệt, lưu vết, chặn phát hành | P0 |
| 15 | Số liệu chứng minh | **Có một phần** | `stats.py` tính bằng code; `check_evidence`; tool trả `id` phản hồi | Test; so tay một bản nháp với số liệu | Xem mục 5.3 | P0 |
| 16 | Tối ưu chi phí | **Có một phần** | Dùng model nhỏ, `max_output_tokens=1024`, thinking tối thiểu, retry tối đa 3 lần | Đọc code | Phân tầng model thật sự, cache, xử lý lô, đo token và chi phí | P1 |
| 17 | Docker, Fly.io | **Chưa có** | — | Tìm trong repo | Toàn bộ | P1 |
| 18 | Kiểm thử, đánh giá | **Có một phần** | 37 test đơn vị; so nhãn trên 9 mẫu | `pytest` pass | Tập đánh giá tiếng Việt; chỉ số cho gom cụm, hotspot, PII, độ trễ, chi phí | P0 |

## 5. Kiểm tra sâu

### 5.1 Privacy

**Có chạy trước LLM và trước khi lưu không?** Có, từ lần refactor này. `pipeline.analyze_feedbacks` che PII rồi mới gọi `classify`, và báo cáo chỉ lưu bản đã che. Test xác nhận cả văn bản LLM nhận được lẫn báo cáo đều không còn tên, số điện thoại và email mẫu. Ở code gốc, hàm che tồn tại nhưng không được gọi. Chưa có embedding hay vector store nên chưa có đường nào khác để kiểm tra.

**Bao phủ đã đủ chưa?** Chưa. Thử 9 câu chứa định danh giả, 8 câu lọt:

| Loại định danh | Kết quả |
| --- | --- |
| Email; số di động dạng `0xxxxxxxxx`, `+84…`, có dấu cách/chấm/gạch | Được che |
| Tên khách hàng khi file có `customer_name` | Được che |
| Tên người không khai báo trước (khách tự xưng tên, tên nhân viên) | Lọt |
| Số bắt đầu `84` không có dấu `+`; dạng `(+84) …` | Lọt |
| Số máy bàn 11 chữ số | Lọt |
| Số CCCD 12 chữ số | Lọt |
| Địa chỉ nhà, số căn hộ | Lọt |
| Đường dẫn tài khoản mạng xã hội | Lọt |
| Số tài khoản ngân hàng 10 chữ số bắt đầu bằng 0 | Bị che thành `[PHONE]` (che được, nhưng sai loại) |

Đây là danh sách thử định tính, chưa phải tỷ lệ lọt đo trên tập kiểm tra.

**Đường rò qua log và lỗi:**

- Thông báo lỗi schema không còn kèm giá trị đầu vào (có test). Thông báo lỗi API lấy từ máy chủ Gemini, chưa thấy trường hợp nào chứa nội dung request nhưng chưa kiểm tra hết các mã lỗi.
- Log khi chạy `analyze` chỉ có id và nhãn. `chat --verbose` in toàn bộ kết quả tool, tức là có văn bản đã che.
- File đầu vào trong `data/` vẫn là bản gốc chưa che. Với dữ liệu mẫu thì không sao; với dữ liệu thật cần vùng lưu riêng có giới hạn truy cập.
- Câu hỏi người dùng gõ vào `chat` được gửi nguyên tới Gemini, không qua bước che.

### 5.2 HITL

Chưa chặn được gì. Hiện chỉ có một dòng chữ in trước bản nháp. Bản nháp không được lưu, không có trạng thái, không có người duyệt, không có thời điểm duyệt. Vì chưa có kênh "áp dụng" hay "phát hành" nào (không API, không dashboard) nên cũng chưa có gì để chặn; cơ chế này phải được xây cùng lúc với kênh phát hành đầu tiên.

Lưu ý thêm: câu trả lời của lệnh `chat` là nội dung AI tạo ra và đến thẳng người dùng. Cần quyết định về mặt sản phẩm xem hỏi đáp có thuộc phạm vi phải duyệt hay không (mục VOC-52 trong backlog).

### 5.3 Số liệu và truy vết

- **Tính từ dữ liệu:** Có. Số đếm và tỷ lệ do `stats.py` tính. LLM viết insight chỉ nhận một JSON gồm tên dự án, tổng số đã phân tích, số tiêu cực, tỷ lệ và số tiêu cực theo chủ đề (có test kiểm tra đúng nội dung gửi đi).
- **Mẫu số:** Có nêu, là số phản hồi phân tích thành công. Số phản hồi lỗi được in riêng.
- **Mã phản hồi:** Từng kết quả giữ `id` và đoạn trích bằng chứng đã được kiểm tra là có trong văn bản. Tool `get_negative_feedback` trả `id`. Bản nháp insight thì **không** kèm danh sách `id`.
- **Phạm vi:** Chỉ có theo dự án. Chưa có theo nguồn (dữ liệu có trường `source` nhưng thống kê chưa dùng) và chưa có theo thời gian.
- **Nguy cơ LLM tự sinh số:** Còn. Prompt yêu cầu chỉ dùng số được cấp, nhưng không có bước nào đối chiếu các con số trong văn bản LLM viết với số liệu gốc. Trong một lần chạy thật, bản nháp cho DuAnA nêu đúng 7, 5, 71,43%, 4 và 1; đó là một lần quan sát, không phải bảo đảm.

### 5.4 Hotspot

Chưa có. Dữ liệu không có trường thời gian nên không thể chia cửa sổ hay dựng đường cơ sở. Thống kê hiện tại chỉ cho biết chủ đề nào có nhiều phản hồi tiêu cực nhất trong toàn bộ dữ liệu, và điều đó không chứng minh được sự gia tăng. Prompt insight đã cấm kết luận "đang gia tăng khi thiếu dữ liệu thời gian", nên hệ thống hiện không tuyên bố sai, nhưng cũng chưa đáp ứng yêu cầu.

### 5.5 Phân loại, gom cụm, LangGraph

- Chỉ có **phân loại vào 6 chủ đề định sẵn**. Không có gom cụm ngữ nghĩa, không có embedding.
- Không có LangGraph. "State" giữa các bước là file báo cáo JSON; trong lệnh `chat` là danh sách lịch sử hội thoại trong bộ nhớ.
- `agent.py` là một agent đơn dùng function calling của Gemini với 2 tool, tối đa 5 lượt gọi mỗi câu hỏi. Đây không phải hệ multi-agent.

### 5.6 Chi phí

| Hạng mục | Hiện trạng |
| --- | --- |
| Phân tầng model | Cấu hình đã tách ba biến (`VOC_CLASSIFIER_MODEL`, `VOC_INSIGHT_MODEL`, `VOC_AGENT_MODEL`) nhưng cả ba mặc định cùng `gemini-3.5-flash-lite` |
| Giới hạn token | `max_output_tokens=1024` cho mọi lời gọi; chưa giới hạn độ dài đầu vào |
| Retry | Tối đa 3 lần thử cho mã 408, 429, 5xx; timeout 60 giây mỗi lần |
| Cache | Chưa có. Chạy lại `analyze` là gọi lại LLM cho mọi phản hồi |
| Xử lý lô, song song | Chưa có. Mỗi phản hồi một lời gọi, tuần tự |
| Theo dõi usage, chi phí | Chưa có. SDK trả `usage_metadata` nhưng code chưa đọc |

Số liệu quan sát được (không phải phép đo có hệ thống): một lời gọi phân loại dùng 248 token đầu vào và 37 token đầu ra, mất 1,86 giây; chạy `analyze` trên 9 phản hồi mất khoảng 16 giây tính cả khởi động. **Chưa có số liệu chi phí.**

## 6. Kết luận

**Làm được gì:** phân loại chủ đề và cảm xúc có bằng chứng trích nguyên văn; thống kê tỷ lệ tiêu cực theo dự án bằng code; viết bản nháp tóm tắt và đề xuất từ số liệu; hỏi đáp có gọi tool; che email và số di động trước khi gọi LLM.

**Kịch bản demo được ngay:**

1. `python -m src analyze` → xem từng phản hồi được gán nhãn và tỷ lệ khớp nhãn mẫu.
2. `python -m src summary --project DuAnA` → xem thống kê và bản nháp insight có số liệu.
3. `python -m src chat` → hỏi "DuAnA bị phàn nàn nhiều nhất về gì? Cho 2 ví dụ", rồi hỏi nối "Còn DuAnB?" để thấy agent tự gọi 2 tool và dùng lịch sử hội thoại.

**Còn thiếu để đạt MVP:** dữ liệu có thời gian với khối lượng đủ lớn; nạp từ nhiều kênh; che tên người và các định danh còn lọt; thống kê theo nguồn và thời gian có kèm ID; phát hiện điểm nóng; báo cáo có cấu trúc được đối chiếu số liệu; quy trình duyệt có lưu trạng thái và chặn phát hành; API; dashboard có drill-down; tập đánh giá.

**Blocker lớn nhất:**

1. **Không có dữ liệu thời gian và khối lượng.** Chín phản hồi không có timestamp thì không định nghĩa được hotspot, không đánh giá được chất lượng, không có gì để drill-down. Mọi tính năng phía sau đều phụ thuộc vào đây.
2. **Chưa có tầng lưu trữ và API.** Trạng thái duyệt, lịch sử lượt chạy và dashboard đều cần nơi lưu bền và một giao diện lập trình. Hiện chỉ có một file JSON bị ghi đè mỗi lần chạy.
3. **Che PII chưa đủ để dùng dữ liệu thật.** Tên người lọt hoàn toàn. Hướng xử lý có ràng buộc: không thể dùng LLM trên cloud để tìm PII vì như vậy là đã gửi PII ra ngoài.
4. **Chưa rõ định dạng và quyền truy cập dữ liệu thật** của CRM, tổng đài, mạng xã hội. Repo không có thông tin này.
5. **Chưa có tập đánh giá**, nên mọi thay đổi prompt hay model đều không đo được tốt lên hay xấu đi.
