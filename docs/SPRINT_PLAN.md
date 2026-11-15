# Kế hoạch phát triển theo sprint

Lập ngày 2026-11-10, cập nhật 15/11/2026, dựa trên code sau refactor và khoảng thiếu hụt so với đề bài ([PROJECT_STATUS.md](PROJECT_STATUS.md)).

## 1. Giả định

Repo không ghi nguồn lực hay hạn chót, nên kế hoạch dùng các giả định sau. Hãy sửa nếu sai.

| Giả định | Giá trị | Ảnh hưởng nếu khác |
| --- | --- | --- |
| Nguồn lực | 1 lập trình viên | Thêm người thì tách song song backend và frontend từ Sprint 4 |
| Độ dài sprint | 1 tuần | — |
| Tốc độ | Chưa biết. Tạm xếp 15–18 điểm mỗi sprint | Sprint 1 dùng để đo; các sprint sau xếp lại theo tốc độ thực tế |
| Dữ liệu thật | Chưa có quyền truy cập, chưa biết định dạng | MVP chạy trên dữ liệu tổng hợp; kết nối kênh thật nằm sau MVP |
| LLM | Tiếp tục dùng Gemini qua `google-genai` | Đổi nhà cung cấp chỉ ảnh hưởng `src/llm.py` |

Điểm là ước lượng tương đối (1, 2, 3, 5, 8), không quy ra giờ. Mục 8 điểm cần spike trước hoặc phải tách nhỏ.

Tổng khối lượng ước tính là 8 sprint: 5 sprint tới MVP, 2 sprint cho phần nâng cao, 1 sprint cho vận hành. Con số này sẽ đổi sau khi biết tốc độ thực tế.

## 2. Phạm vi sản phẩm

### Mức 1: MVP demo xuyên suốt (Sprint 1–5)

Một quản lý mở dashboard, thấy điểm nóng của từng dự án kèm số liệu, bấm vào để xem phản hồi gốc đã che, đọc bản nháp báo cáo và đề xuất, rồi duyệt. Chỉ nội dung đã duyệt mới hiển thị ở khu vực phát hành.

Hoàn thành khi, trên bộ dữ liệu tổng hợp (ít nhất 300 phản hồi, 4 nguồn, 3 dự án, 8 tuần):

1. Một lệnh hoặc một lời gọi API chạy trọn chuỗi nạp → che PII → phân loại → thống kê → hotspot → bản nháp báo cáo → chờ duyệt.
2. Tỷ lệ lọt PII được đo theo từng loại định danh và đạt ngưỡng đã thống nhất.
3. Mọi con số trên dashboard và trong báo cáo đi kèm mẫu số, phạm vi (dự án, khoảng thời gian, nguồn) và danh sách ID phản hồi mở ra được.
4. Điểm nóng cài sẵn trong dữ liệu được phát hiện; chuỗi ổn định không bị báo; nhóm ít mẫu được đánh dấu "không đủ mẫu".
5. Có test chứng minh báo cáo chưa duyệt không lấy được qua endpoint phát hành; bản đã duyệt lưu người duyệt và thời điểm.
6. Trên dashboard, bấm biểu đồ tổng → dự án → khoảng thời gian → danh sách phản hồi.
7. Có lệnh đánh giá cho ra chỉ số chủ đề và cảm xúc trên tập gán nhãn tay.

Che PII, số liệu truy vết được và HITL đều nằm trong luồng này từ sớm: che PII và đo lọt ở Sprint 1, số liệu truy vết ở Sprint 1, báo cáo đối chiếu số ở Sprint 3, chặn phát hành ở Sprint 4.

### Mức 2: Yêu cầu nâng cao (Sprint 6–7)

Gom cụm ngữ nghĩa bằng embedding, lưu và tìm kiếm trên vector database, agent tổng hợp đọc theo cụm, phân tầng model có số đo chi phí.

Hoàn thành khi: chất lượng gom cụm được đo trên tập đánh giá và đạt ngưỡng đã thống nhất; báo cáo trích được cụm và ID phản hồi trong cụm; có bảng chi phí trên 1.000 phản hồi trước và sau phân tầng.

### Mức 3: Hoàn thiện để vận hành (Sprint 8 trở đi)

Nạp từ định dạng xuất thật của từng kênh, đăng nhập và phân quyền, Docker, triển khai Fly.io, lưu vết phiên bản báo cáo, giám sát.

Hoàn thành khi: bản triển khai trên Fly.io chạy được kịch bản demo; một file xuất thật của mỗi kênh nạp được; chỉ vai trò quản lý mới duyệt được.

## 3. Product Backlog

Cột "Loại": **S** là user story, **E** là enabler kỹ thuật, **Sp** là spike có giới hạn thời gian. Cột "ƯT": P0 thuộc MVP, P1 nâng cao hoặc vận hành, P2 để sau.

### Epic A: Dữ liệu và thu thập

| ID | Loại | Nội dung | Hiện trạng | Tiêu chí nghiệm thu | Phụ thuộc | ƯT | Điểm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VOC-01 | E | Thêm thời điểm phản hồi (`created_at`) và nguồn `call_center` vào schema | `Feedback` chưa có thời gian; `Source` có 3 giá trị | Bản ghi thiếu hoặc sai thời gian bị loại kèm `id`; thời gian lưu theo UTC; báo cáo giữ `created_at` | — | P0 | 2 |
| VOC-02 | E | Bộ dữ liệu tổng hợp tái lập được | Chỉ có 9 phản hồi mẫu | Script có seed sinh ≥300 phản hồi, 4 nguồn, 3 dự án, 8 tuần, một điểm nóng cài sẵn, PII giả kèm bảng kê; không có định danh thật | VOC-01 | P0 | 3 |
| VOC-03 | S | Là chuyên viên CSKH, tôi muốn nạp file CSV/JSON xuất từ khảo sát, CRM, mạng xã hội và tổng đài, để mọi phản hồi về một nơi | Chỉ đọc một file JSON đúng schema | Ánh xạ cột khai báo theo từng kênh; nạp lại cùng file không tạo bản ghi trùng; có báo cáo dòng lỗi | VOC-01, VOC-05 | P0 | 5 |
| VOC-04 | Sp | Khảo sát định dạng xuất thật của từng kênh (nửa ngày) | Chưa có thông tin | Tài liệu ánh xạ trường cho từng kênh; danh sách trường chứa PII | Có file mẫu thật | P1 | 1 |
| VOC-05 | E | Lưu trữ bền thay file JSON: phản hồi, kết quả, lượt chạy, báo cáo, lượt duyệt | `storage.py` ghi đè một file | Chạy lại không nhân đôi dữ liệu; đổi được giữa SQLite và Postgres qua cấu hình; test đọc/ghi | VOC-01 | P0 | 5 |
| VOC-06 | E | Thu thập đánh giá thật từ Google Maps cho 3 dự án | **Xong 15/11.** Công cụ ở `E:\VoC-data-collector` (ngoài repo vì chứa tên dự án thật và bản gốc); 1.202 đánh giá thô → 164 câu dùng được | Có file JSON đã ẩn danh mà `python -m src analyze` đọc được; không lưu tên người đánh giá | — | P0 | 3 |

### Epic B: Quyền riêng tư

| ID | Loại | Nội dung | Hiện trạng | Tiêu chí nghiệm thu | Phụ thuộc | ƯT | Điểm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VOC-10 | E | Mở rộng regex: số `84…`, `(+84)`, máy bàn, CCCD/CMND, đường dẫn tài khoản MXH | 8/9 ca thử lọt (PROJECT_STATUS mục 5.1) | Năm ca lọt thuộc phạm vi regex trở thành test và pass; có ca chống che nhầm giá tiền, ngày, số hợp đồng. Tên người và địa chỉ thuộc VOC-11 | — | P0 | 2 |
| VOC-11 | S | Là người phụ trách dữ liệu, tôi muốn tên người và địa chỉ được che dù không khai báo trước, để dữ liệu thật dùng được | Tên chỉ che khi có `customer_name` | Recall che tên trên tập kiểm tra đạt ngưỡng đã thống nhất; tỷ lệ che nhầm được báo cáo; chạy cục bộ, không gửi văn bản ra ngoài | VOC-12, VOC-13 | P0 | 5 |
| VOC-12 | Sp | Chọn cách nhận diện tên tiếng Việt chạy cục bộ (1 ngày) | Chưa có | So ít nhất 2 phương án trên 50 câu: recall, che nhầm, tốc độ, kích thước cài đặt; có khuyến nghị | VOC-13 | P0 | 1 |
| VOC-13 | E | Đo tỷ lệ lọt PII | Chưa đo | Lệnh đối chiếu báo cáo với bảng kê PII, in tỷ lệ lọt theo loại; kết quả đầu tiên được ghi lại | VOC-02 | P0 | 2 |
| VOC-14 | E | Vùng lưu bản gốc có giới hạn truy cập; che PII trong câu hỏi chat | File gốc nằm chung `data/`; câu hỏi chat gửi nguyên | Pipeline chỉ đọc bản đã che từ kho chính; test xác nhận câu hỏi chat đã che trước khi gửi | VOC-05 | P1 | 3 |

### Epic C: Phân tích và gom cụm

| ID | Loại | Nội dung | Hiện trạng | Tiêu chí nghiệm thu | Phụ thuộc | ƯT | Điểm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VOC-20 | E | Ghi thông tin lượt chạy: mã lượt, model, mã băm prompt, thời gian, số đầu vào/thành công/lỗi, token | Báo cáo chỉ có `results` và `errors`; chưa đọc `usage_metadata` | Mỗi báo cáo có khối thông tin lượt chạy; tổng token khớp tổng từng lời gọi; báo cáo cũ vẫn đọc được | — | P0 | 2 |
| VOC-21 | E | Chỉ phân tích bản ghi mới, gọi song song có giới hạn, cache theo nội dung | Tuần tự, khoảng 1,8 giây mỗi phản hồi; chạy lại là gọi lại hết | Chạy lại trên dữ liệu không đổi không phát sinh lời gọi LLM; thời gian xử lý 300 phản hồi được đo trước và sau | VOC-05, VOC-20, VOC-28 | P1 | 4 |
| VOC-22 | Sp | Chọn model embedding cho tiếng Việt và thuật toán gom cụm (1,5 ngày) | Chưa có | So ít nhất 2 model và 2 thuật toán trên tập đánh giá gom cụm; có khuyến nghị và ngưỡng đề xuất | VOC-74 | P1 | 2 |
| VOC-23 | S | Là quản lý, tôi muốn các phản hồi cùng ý được gom thành nhóm có tên, để thấy vấn đề cụ thể bên trong mỗi chủ đề | Chỉ có 6 chủ đề cố định | Chỉ số gom cụm đạt ngưỡng từ VOC-22; mỗi cụm có tên, số lượng, danh sách ID; embedding tạo từ văn bản đã che | VOC-22, VOC-24 | P1 | 8 |
| VOC-24 | E | Vector database lưu embedding và tìm phản hồi tương tự | Chưa có | Truy vấn "phản hồi giống phản hồi X" trả kết quả kèm ID; chỉ lưu văn bản đã che | VOC-05 | P1 | 5 |
| VOC-25 | S | Là quản lý, tôi muốn một phản hồi nói về nhiều khía cạnh được ghi nhận đủ | Mỗi phản hồi chỉ một chủ đề chính | Cần spike trước khi viết tiêu chí | VOC-70 | P2 | 5 |
| VOC-26 | E | Thêm chủ đề `location_infrastructure` và ghi ranh giới chủ đề trong prompt | **Xong 15/11** (schema, prompt, test pass, đã đo lại). Chủ đề khớp nhãn tăng từ 70,6% lên 79,8%; tác dụng phụ: recall `sales_service` giảm từ 0,88 xuống 0,56 | Kết quả đo lại trên 164 câu thật được ghi thành mục mới trong `EVAL_RESULTS.md` | VOC-06 | P0 | 1 |
| VOC-27 | E | Prompt: câu khen chê lẫn lộn lấy ý chê; làm rõ thái độ bảo vệ, ban quản lý thuộc `sales_service` hay `other` | 9/13 lỗi cảm xúc ngày 15/11 là câu khen chê lẫn lộn; luật này có trong hướng dẫn gán nhãn nhưng chưa có trong prompt | Chỉ chỉnh trên phần dev; recall tiêu cực trên phần test được ghi lại; F1 các lớp khác không giảm quá mức đã thống nhất | VOC-70, VOC-71 | P0 | 2 |
| VOC-28 | E | Giới hạn tốc độ gọi LLM, cấu hình được (mặc định 15 lời gọi/phút) | Ngày 15/11, 35/164 lời gọi lỗi 429 vì vượt giới hạn của gói miễn phí; đang phải đặt `VOC_RETRY_ATTEMPTS=8` | Chạy 164 câu thật với retry mặc định không có lỗi 429; có test với đồng hồ giả | — | P0 | 1 |

### Epic D: Số liệu và điểm nóng

| ID | Loại | Nội dung | Hiện trạng | Tiêu chí nghiệm thu | Phụ thuộc | ƯT | Điểm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VOC-30 | S | Là quản lý, tôi muốn xem số liệu theo dự án, chủ đề, cảm xúc, nguồn và khoảng thời gian, kèm mẫu số và ID phản hồi, để kiểm chứng được | `stats.py` chỉ có tổng và số tiêu cực theo dự án | Mỗi ô số liệu có số đếm, tỷ lệ, mẫu số, phạm vi lọc, danh sách ID; tổng các ô bằng mẫu số; phạm vi rỗng không gây lỗi chia | VOC-01 | P0 | 3 |
| VOC-31 | S | Là quản lý, tôi muốn được báo khi tỷ lệ tiêu cực của một chủ đề tại một dự án tăng bất thường so với trước đó | Chưa có; dữ liệu chưa có thời gian | So cửa sổ gần nhất với đường cơ sở, nêu số đếm và mẫu số của cả hai; dưới cỡ mẫu tối thiểu thì trả "không đủ mẫu"; phát hiện điểm nóng cài sẵn; không báo trên chuỗi ổn định; tính bằng code, không dùng LLM | VOC-02, VOC-30 | P0 | 5 |

### Epic E: Tổng hợp, đề xuất và điều phối

| ID | Loại | Nội dung | Hiện trạng | Tiêu chí nghiệm thu | Phụ thuộc | ƯT | Điểm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VOC-40 | Sp | Thử LangGraph: state có kiểu, điểm dừng chờ người duyệt, lưu và tiếp tục lượt chạy (1 ngày) | Chưa dùng LangGraph | Mẫu chạy được 3 node, dừng chờ duyệt rồi tiếp tục sau khi khởi động lại tiến trình; ghi lại cách gọi `src.llm` từ node | — | P0 | 1 |
| VOC-41 | E | Chuyển pipeline sang đồ thị LangGraph: nạp → che → phân loại → thống kê → hotspot → tổng hợp → đề xuất → chờ duyệt | Các hàm Python gọi nối tiếp qua CLI | Một lời gọi chạy trọn đồ thị; state mỗi bước kiểm tra được; node tái dùng hàm trong `src/`; lỗi ở một node không làm mất kết quả các node trước | VOC-40, VOC-05, VOC-31 | P0 | 5 |
| VOC-42 | S | Là quản lý, tôi muốn báo cáo insight mà mỗi nhận định đều kèm số liệu và ID bằng chứng, để tin được | `generate_insight` trả văn bản tự do, không đối chiếu số | Output có cấu trúc: từng nhận định trỏ tới chỉ số và ID; bộ kiểm tra bằng code đối chiếu mọi con số với thống kê, sai thì loại; đầu báo cáo ghi phạm vi phân tích theo nguồn | VOC-30, VOC-31 | P0 | 5 |
| VOC-43 | S | Là quản lý, tôi muốn nhận đề xuất hành động có thứ tự ưu tiên và cảnh báo rủi ro truyền thông khi có điểm nóng | Tối đa 2 đề xuất dạng văn bản, không gắn nguồn | Mỗi đề xuất trỏ tới điểm nóng hoặc nhận định nguồn; không có điểm nóng thì không sinh cảnh báo; đề xuất ở trạng thái nháp | VOC-42 | P0 | 3 |
| VOC-44 | E | Phân tầng model: model nhỏ cho phân loại, model lớn hơn cho tổng hợp và đề xuất | Cấu hình đã tách 3 biến model, cùng mặc định | Chỉ số chất lượng và chi phí trên 1.000 phản hồi của hai cấu hình được ghi lại; cấu hình mặc định chọn theo số đo | VOC-71, VOC-75 | P1 | 2 |
| VOC-45 | S | Là quản lý, tôi muốn báo cáo nêu các vấn đề cụ thể rút từ từng cụm phản hồi | Báo cáo chỉ dựa trên số đếm theo chủ đề | Mỗi insight trỏ tới cụm và ID trong cụm; qua được bộ kiểm tra của VOC-42 | VOC-23, VOC-42 | P1 | 3 |

### Epic F: Kiểm duyệt con người

| ID | Loại | Nội dung | Hiện trạng | Tiêu chí nghiệm thu | Phụ thuộc | ƯT | Điểm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VOC-50 | S | Là quản lý, tôi muốn duyệt, yêu cầu sửa hoặc từ chối từng báo cáo và đề xuất trước khi phát hành | Chỉ có một dòng chữ "BẢN NHÁP" | Trạng thái nháp → chờ duyệt → đã duyệt hoặc từ chối; lưu người duyệt, thời điểm, ghi chú; endpoint phát hành chỉ trả bản đã duyệt (có test); sửa nội dung sau khi duyệt đưa về chờ duyệt | VOC-05, VOC-41 | P0 | 5 |
| VOC-51 | E | Lịch sử phiên bản và nhật ký duyệt | Chưa có | Xem được ai đổi gì, khi nào; bản đã duyệt không bị ghi đè | VOC-50 | P1 | 2 |
| VOC-52 | — | Quyết định sản phẩm: câu trả lời của chat có thuộc diện phải duyệt không | Chat trả lời thẳng người dùng | Có quyết định bằng văn bản; nếu có thì tạo story tương ứng | — | P1 | 1 |

### Epic G: API và dashboard

| ID | Loại | Nội dung | Hiện trạng | Tiêu chí nghiệm thu | Phụ thuộc | ƯT | Điểm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VOC-60 | E | FastAPI chỉ-đọc: kiểm tra sức khỏe, số liệu, danh sách phản hồi đã che | Chỉ có CLI | Endpoint trả cùng số liệu với CLI; có test; tài liệu OpenAPI mở được | VOC-30 | P0 | 2 |
| VOC-61 | E | API ghi: nạp dữ liệu, khởi chạy phân tích, điểm nóng, báo cáo, duyệt | Chưa có | Chạy được kịch bản MVP chỉ bằng API; thao tác duyệt yêu cầu danh tính người duyệt | VOC-41, VOC-50, VOC-60 | P0 | 3 |
| VOC-62 | S | Là quản lý, tôi muốn một trang tổng quan theo dự án với biểu đồ chủ đề và cảm xúc cùng các điểm nóng | Chưa có frontend | Biểu đồ dùng số từ API; mỗi số hiển thị mẫu số và khoảng thời gian | VOC-60, VOC-64 | P0 | 3 |
| VOC-63 | S | Là quản lý, tôi muốn bấm vào biểu đồ để đào sâu theo dự án và khoảng thời gian tới từng phản hồi | Chưa có | Bấm cột biểu đồ → lọc theo dự án → chọn khoảng thời gian → danh sách phản hồi đã che kèm bằng chứng; trạng thái lọc nằm trên URL | VOC-62 | P0 | 5 |
| VOC-64 | S | Là quản lý, tôi muốn một màn hình hàng chờ duyệt để đọc bản nháp cạnh số liệu rồi quyết định | Chưa có | Xem bản nháp, số liệu và bằng chứng trên một màn hình; duyệt hoặc từ chối cập nhật trạng thái; gồm việc dựng khung Next.js | VOC-61 | P0 | 5 |
| VOC-65 | E | Đăng nhập và vai trò chuyên viên, quản lý | Chưa có | Chỉ quản lý duyệt được; người duyệt lấy từ phiên đăng nhập | VOC-50 | P1 | 3 |

### Epic H: Đánh giá AI

| ID | Loại | Nội dung | Hiện trạng | Tiêu chí nghiệm thu | Phụ thuộc | ƯT | Điểm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VOC-70 | E | Tập đánh giá tiếng Việt gán nhãn tay cho phản hồi bất động sản | **Một phần (15/11):** 164 đánh giá Google Maps, nhãn do Claude gán và người dùng chấp nhận cả bộ. Còn thiếu: duyệt tay, tách dev/test, mẫu cho `legal_process` (0), `construction_progress` (6), `neutral` (2), và các kênh ngoài mạng xã hội | Duyệt tay ít nhất các câu khen chê lẫn lộn và câu `other`; tách dev/test cố định; 50 mẫu gán hai lượt để đo độ đồng thuận; lớp nào dưới 15 mẫu thì bổ sung hoặc ghi rõ không đo được | VOC-06 | P0 | 2 |
| VOC-71 | E | Lệnh `evaluate`: chỉ số theo lớp, ma trận nhầm lẫn, ghi kết quả kèm model và mã băm prompt | Chỉ số ngày 15/11 được tính bằng script tạm ngoài repo; `summarize_evaluation` chỉ đếm số đúng | Lệnh tái lập được các mục đã có trong `docs/EVAL_RESULTS.md`; kết quả mới ghi kèm model, mã băm prompt, phiên bản tập đánh giá | VOC-20, VOC-70 | P0 | 2 |
| VOC-72 | E | Đánh giá hotspot trên chuỗi tổng hợp có và không có điểm nóng | Chưa có | Báo cáo recall, số báo nhầm, độ trễ phát hiện qua nhiều seed | VOC-31 | P0 | 2 |
| VOC-73 | E | Đo tính có căn cứ của báo cáo | Chưa có | Tỷ lệ báo cáo qua bộ kiểm tra số liệu và tỷ lệ nhận định có ID hợp lệ được ghi lại; soát tay 20 nhận định | VOC-42 | P0 | 2 |
| VOC-74 | E | Tập và chỉ số đánh giá gom cụm | Chưa có | Tập con có nhãn vấn đề chi tiết; script tính chỉ số; quy trình soát tay độ mạch lạc của cụm | VOC-70 | P1 | 3 |
| VOC-75 | E | Báo cáo độ trễ và chi phí | Chỉ có vài số quan sát lẻ | p50/p95 mỗi phản hồi, token và chi phí trên 1.000 phản hồi, tính từ thông tin lượt chạy | VOC-20 | P1 | 2 |

### Epic I: Triển khai và vận hành

| ID | Loại | Nội dung | Hiện trạng | Tiêu chí nghiệm thu | Phụ thuộc | ƯT | Điểm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VOC-80 | E | Dockerfile cho backend và frontend, docker-compose kèm database | Chưa có | Một lệnh dựng được toàn bộ; kịch bản demo chạy trong container | VOC-61, VOC-63 | P1 | 3 |
| VOC-81 | E | Triển khai Fly.io | Chưa có | Bản triển khai chạy được kịch bản demo; secret đặt qua Fly, không nằm trong image | VOC-80 | P1 | 3 |
| VOC-82 | E | CI chạy pytest và ruff khi push | Chưa có; repo đã ở GitHub | Push làm chạy kiểm tra; lỗi thì báo đỏ | — | P1 | 1 |
| VOC-83 | E | Log có cấu trúc không chứa PII, theo dõi tỷ lệ lỗi | Log in ra console | Cần làm rõ khi gần triển khai | VOC-81 | P2 | 2 |
| VOC-84 | E | Dọn repo: commit phần refactor, xóa file lạ `er.name Ten cua ban` | Thay đổi chưa commit | `git status` sạch; test pass trên nhánh chính | — | P0 | 1 |
| VOC-85 | E | Kịch bản demo MVP và sửa lỗi tích hợp | — | Kịch bản mục 2 chạy trọn từ dữ liệu trắng, có ghi lại từng bước | Các mục P0 | P0 | 2 |

### Các điểm cần spike

| Spike | Câu hỏi cần trả lời | Khuyến nghị ban đầu, chờ kiểm chứng |
| --- | --- | --- |
| VOC-12 | Nhận diện tên người tiếng Việt bằng gì mà không gửi dữ liệu ra ngoài? | Thử thư viện NER tiếng Việt chạy cục bộ và danh sách họ phổ biến kết hợp từ xưng hô. Không dùng LLM trên cloud cho việc này |
| VOC-40 | LangGraph có giữ được lượt chạy đang chờ duyệt qua lần khởi động lại không? Gọi `src.llm` từ node thế nào? | Node gọi thẳng hàm trong `src/`, không cần lớp bọc model của LangChain |
| VOC-22 | Model embedding và thuật toán nào gom cụm tốt cho phản hồi tiếng Việt ngắn? | Chưa có; quyết định bằng số đo trên tập đánh giá |
| VOC-05 (quyết định trong lúc làm) | SQLite hay Postgres? Vector database nào? | Sprint 2 dùng SQLite qua một tầng truy cập trừu tượng để không phải cài gì; chuyển Postgres + pgvector ở Sprint 6 để dùng chung một database cho dữ liệu quan hệ và vector |
| VOC-04 | Mỗi kênh xuất dữ liệu ra định dạng nào, trường nào chứa PII? | Cần file mẫu thật mới làm được |

## 4. Kế hoạch sprint

### Tiến độ thực tế (cập nhật 15/11/2026, hết ngày 1 của Sprint 1)

| Nhóm | Mục | Trạng thái |
| --- | --- | --- |
| Kế hoạch Sprint 1 | VOC-84, 01, 02, 10, 13, 20, 30 | VOC-84 gần xong: đã commit và push lên nhánh `sprint1/refactor-va-danh-gia-du-lieu-that`, chưa gộp vào `main`. Các mục còn lại chưa bắt đầu |
| Ngoài kế hoạch, đã xong | VOC-06 (thu thập dữ liệu thật), VOC-26 (chủ đề mới) | 4 điểm |
| Làm sớm một phần | VOC-70 (164 câu có nhãn, chưa duyệt tay, chưa tách dev/test); VOC-71 (đã có số đo, chưa có lệnh trong repo) | Phần còn lại ở Sprint 2 |
| Phát sinh từ số đo | VOC-27 (luật khen chê lẫn lộn), VOC-28 (giới hạn tốc độ gọi) | VOC-28 vào Sprint 1, VOC-27 vào Sprint 2 |

Thay đổi so với kế hoạch ban đầu: VOC-60 dời từ Sprint 1 sang Sprint 3 để nhường chỗ cho VOC-28; VOC-12 dời từ Sprint 2 sang Sprint 3 để nhường chỗ cho VOC-27; VOC-21 giảm còn 4 điểm vì phần giới hạn tốc độ tách thành VOC-28.

| Sprint | Mục tiêu | Mục backlog | Điểm |
| --- | --- | --- | --- |
| 1 | Số liệu có thời gian, truy vết được, đo được lọt PII | VOC-84, 01, 02, 10, 13, 20, 30, 28. Đã xong ngoài kế hoạch: VOC-06, 26 | 16 còn lại + 4 đã xong |
| 2 | Phát hiện điểm nóng trên dữ liệu lưu bền; có baseline chất lượng | VOC-05, 31, 72, 71, 70 (phần còn lại), 27 | 18 |
| 3 | Báo cáo và đề xuất có căn cứ, chạy trong đồ thị LangGraph | VOC-40, 41, 42, 43, 73, 60, 12 | 19 |
| 4 | Không gì được phát hành khi chưa duyệt; tên người được che | VOC-50, 61, 64, 11 | 18 |
| 5 | Dashboard drill-down; nạp đa kênh; **demo MVP** | VOC-62, 63, 03, 82, 85 | 16 |
| 6 | Nền cho gom cụm: tập đánh giá, chọn model, tìm kiếm tương tự; xử lý tăng dần | VOC-74, 22, 24, 21 | 14 |
| 7 | Gom cụm ngữ nghĩa, insight theo cụm, chi phí được đo | VOC-23, 45, 75, 44 | 15 |
| 8 | Triển khai và kênh thật | VOC-04, 14, 65, 80, 81, 51 | 15 |

Chưa xếp: VOC-25, VOC-52, VOC-83.

### Sprint 1: Số liệu có thời gian, truy vết được, đo được lọt PII

**Mục tiêu.** Trên 300 phản hồi tổng hợp có PII giả, quản lý hỏi được "dự án B, tháng 9, kênh CRM: bao nhiêu phản hồi tiêu cực về tiến độ, trên tổng bao nhiêu, là những phản hồi nào" và nhận con số kèm ID; đồng thời biết được bao nhiêu PII đã lọt qua bước che.

**Giá trị.** Lần đầu có số liệu theo thời gian và nguồn mà người đọc tự kiểm chứng được, và lần đầu có con số về mức an toàn dữ liệu.

**Điều kiện bắt đầu.** `GEMINI_API_KEY` còn hạn mức cho khoảng 300–600 lời gọi; đồng ý với các giả định ở mục 1.

**Việc cần làm, tiêu chí nghiệm thu, kịch bản demo và lịch:** xem [SPRINT_1_CHECKLIST.md](SPRINT_1_CHECKLIST.md). Sprint 1 gồm 8 mục: VOC-84, 01, 02, 10, 13, 20, 30, 28.

**Rủi ro.**

- Gói Gemini miễn phí giới hạn 15 lời gọi/phút, nên 360 phản hồi mất khoảng 24 phút. VOC-28 xử lý việc này; nếu vẫn nghẽn thì chạy trên tập con.
- Câu sinh từ mẫu dễ phân loại hơn câu thật. Tỷ lệ khớp nhãn trên bộ tổng hợp là cận trên; số đo trên dữ liệu thật nằm ở `EVAL_RESULTS.md`.
- Regex CCCD dễ che nhầm số tiền. Giảm rủi ro bằng cách yêu cầu từ khóa ngữ cảnh và có test chống che nhầm.

### Sprint 2: Phát hiện điểm nóng trên dữ liệu lưu bền

- **Mục tiêu và giá trị.** Hệ thống tự chỉ ra dự án và chủ đề đang xấu đi bất thường, kèm số liệu của cả kỳ hiện tại lẫn kỳ so sánh. Có baseline chất lượng phân loại đầu tiên trên dữ liệu gán nhãn tay.
- **Việc chính.** Tầng lưu trữ sau `storage.py` (VOC-05); thuật toán hotspot bằng code thuần với cỡ mẫu tối thiểu (VOC-31) và đánh giá trên nhiều seed (VOC-72); lệnh `evaluate` (VOC-71), đưa cách tính đang dùng trong script tạm vào repo; hoàn thiện tập đánh giá (VOC-70): duyệt tay, tách dev/test, bổ sung lớp thiếu; luật khen chê lẫn lộn trong prompt (VOC-27), làm sau khi đã tách dev/test.
- **Tái sử dụng.** Bộ dữ liệu và điểm nóng cài sẵn từ Sprint 1; `summarize_evaluation`; hàm thống kê có lọc thời gian.
- **Phụ thuộc và điều kiện bắt đầu.** VOC-01, 02, 30 xong. Thống nhất độ dài cửa sổ và đường cơ sở mặc định (đề xuất: 7 ngày so với 28 ngày trước đó).
- **Nghiệm thu và kiểm thử.** Điểm nóng cài sẵn được phát hiện; chuỗi ổn định qua nhiều seed không bị báo quá ngưỡng đã thống nhất; nhóm dưới cỡ mẫu tối thiểu trả "không đủ mẫu"; chạy lại phân tích không nhân đôi bản ghi; baseline ghi trong `EVAL_RESULTS.md`.
- **Demo.** Chạy lệnh hotspot: thấy điểm nóng với "kỳ này x/n so với kỳ trước y/m"; đổi sang dự án ổn định thì không có cảnh báo; mở kết quả `evaluate`.
- **Bàn giao.** Database, lệnh hotspot, lệnh `evaluate`, tập đánh giá đã duyệt và tách dev/test, số đo trước và sau VOC-27.
- **Rủi ro.** Ngưỡng hotspot chỉnh trên dữ liệu tổng hợp có thể không hợp với dữ liệu thật, nên để ngưỡng trong cấu hình. Gán nhãn tay tốn thời gian hơn dự kiến.

### Sprint 3: Báo cáo và đề xuất có căn cứ, chạy trong đồ thị

- **Mục tiêu và giá trị.** Một lần chạy cho ra bản nháp báo cáo mà mọi con số đã được đối chiếu tự động, cùng đề xuất hành động gắn với điểm nóng.
- **Việc chính.** Spike LangGraph (VOC-40) làm trong ngày đầu; dựng đồ thị từ các hàm sẵn có (VOC-41); output có cấu trúc và bộ kiểm tra số liệu (VOC-42); đề xuất và cảnh báo (VOC-43); đo tính có căn cứ (VOC-73). Thêm hai mục dời sang: API chỉ-đọc (VOC-60, từ Sprint 1) và spike nhận diện tên (VOC-12, từ Sprint 2). Sprint này đang ở 19 điểm, cao hơn mức xếp; sẽ cắt bớt khi biết tốc độ thực tế của Sprint 1.
- **Tái sử dụng.** `pipeline`, `stats`, `llm.generate`, cách ép JSON schema đang dùng cho phân loại.
- **Phụ thuộc và điều kiện bắt đầu.** VOC-05, 31 xong. Nếu spike cho thấy LangGraph không giữ được trạng thái chờ duyệt như cần, ghi lại và chọn cách lưu trạng thái trong database.
- **Nghiệm thu và kiểm thử.** Báo cáo có con số sai bị bộ kiểm tra loại (test với LLM giả cố ý trả số sai); mọi nhận định có ID tồn tại và thuộc đúng phạm vi; đồ thị dừng ở bước chờ duyệt.
- **Demo.** Chạy đồ thị trên dữ liệu có điểm nóng; mở bản nháp, bấm từ một nhận định tới số liệu và ID; cho xem một bản bị loại vì sai số.
- **Bàn giao.** Đồ thị LangGraph, schema báo cáo, bộ kiểm tra, số đo tính có căn cứ.
- **Rủi ro.** Model nhỏ có thể không tuân thủ schema phức tạp; phương án dự phòng là dùng model lớn hơn cho riêng bước này (kéo theo VOC-44).

### Sprint 4: Không gì được phát hành khi chưa duyệt

- **Mục tiêu và giá trị.** Quản lý duyệt báo cáo trên giao diện; nội dung chưa duyệt không thể lọt ra kênh phát hành. Tên người được che, mở đường cho dữ liệu thật.
- **Việc chính.** Trạng thái và lượt duyệt (VOC-50); API ghi (VOC-61); khung Next.js và màn hình hàng chờ duyệt (VOC-64); che tên theo kết quả spike (VOC-11).
- **Phụ thuộc và điều kiện bắt đầu.** VOC-41 xong; có khuyến nghị từ VOC-12. Trước khi có VOC-65, danh tính người duyệt lấy từ một danh sách người dùng cố định trong cấu hình.
- **Nghiệm thu và kiểm thử.** Test: gọi endpoint phát hành với báo cáo ở trạng thái nháp, chờ duyệt, từ chối đều không trả nội dung; sau khi duyệt mới trả, kèm người duyệt và thời điểm. Chỉ số che tên đạt ngưỡng đã thống nhất.
- **Demo.** Mở hàng chờ, đọc bản nháp cạnh số liệu, từ chối một bản kèm ghi chú, duyệt một bản; cho thấy khu vực phát hành chỉ có bản đã duyệt.
- **Rủi ro.** Đây là sprint nặng nhất và là lần đầu dựng frontend. Nếu quá tải, VOC-11 lùi sang Sprint 5, với điều kiện không nạp dữ liệu thật trước khi nó xong.

### Sprint 5: Dashboard drill-down, nạp đa kênh, demo MVP

- **Mục tiêu và giá trị.** Hoàn tất kịch bản MVP ở mục 2.
- **Việc chính.** Trang tổng quan (VOC-62); drill-down (VOC-63); nạp file theo kênh với ánh xạ cột (VOC-03); CI (VOC-82); kịch bản demo và sửa lỗi tích hợp (VOC-85).
- **Nghiệm thu và kiểm thử.** Bảy tiêu chí MVP ở mục 2, chạy từ database trắng.
- **Demo.** Toàn bộ kịch bản MVP, do người không viết code thao tác nếu có thể.
- **Rủi ro.** Ánh xạ cột dựa trên định dạng giả định; định dạng thật chờ VOC-04.

### Sprint 6–8 (khái quát, cập nhật sau mỗi Sprint Review)

- **Sprint 6, nền cho gom cụm.** Dựng tập và chỉ số đánh giá gom cụm trước, rồi spike chọn embedding và thuật toán trên tập đó; dựng vector database; xử lý tăng dần và cache. Demo: tìm phản hồi tương tự một phản hồi cho trước; trình bày số đo của spike; chạy lại phân tích trên dữ liệu không đổi mà không phát sinh lời gọi LLM.
- **Sprint 7, gom cụm và insight theo cụm.** Clustering Agent theo kết quả spike; agent tổng hợp đọc theo cụm; báo cáo độ trễ và chi phí; phân tầng model có số đo. Demo: mở chủ đề "thái độ phục vụ" thấy các cụm như "phản hồi chậm", "hẹn không gọi lại" kèm số lượng và ID; bảng chi phí trên 1.000 phản hồi trước và sau phân tầng. Rủi ro lớn nhất của cả kế hoạch nằm ở mục gom cụm 8 điểm vì chưa có số đo nào; spike ở Sprint 6 là để giảm rủi ro đó, và mục này có thể phải tách sau spike.
- **Sprint 8, triển khai và kênh thật.** Docker, Fly.io, đăng nhập và vai trò, vùng lưu bản gốc, khảo sát và nạp định dạng thật, lịch sử duyệt. Demo: kịch bản MVP trên bản triển khai. Điều kiện: có file xuất thật và tài khoản Fly.io.

## 5. Cách làm việc

### Definition of Ready

Một mục được đưa vào sprint khi:

- Giá trị và tiêu chí nghiệm thu viết ra được và kiểm tra được.
- Các mục phụ thuộc đã xong, hoặc spike liên quan đã có kết luận.
- Dữ liệu hoặc fixture cần để kiểm thử đã có.
- Ước lượng không quá 5 điểm; lớn hơn thì tách hoặc spike trước.
- Với mục có AI: đã biết đo bằng chỉ số nào, trên tập nào.

### Definition of Done

- Code ở nhánh chính; `pytest` và `ruff` pass.
- Tiêu chí nghiệm thu được chứng minh bằng test hoặc bằng bước demo có ghi lại.
- Log, báo cáo và fixture không chứa PII thật hay secret.
- Con số hiển thị cho người dùng do code tính, có mẫu số.
- Thay đổi prompt hoặc model: đã chạy lại `evaluate` và ghi kết quả.
- README và tài liệu được cập nhật nếu lệnh chạy hoặc hành vi thay đổi.

### Nhịp làm việc cho nhóm nhỏ

| Hoạt động | Khi nào | Cách làm |
| --- | --- | --- |
| Planning | Đầu tuần, 30–45 phút | Chốt một câu Sprint Goal; kéo các mục đạt Definition of Ready theo thứ tự ưu tiên, tới mức điểm của sprint trước |
| Cập nhật tiến độ | Mỗi ngày, 5 phút | Ghi ba dòng (đã xong, làm tiếp, vướng gì) vào GitHub Issue của sprint hoặc `docs/SPRINT_LOG.md` |
| Review | Cuối tuần, 30 phút | Chạy kịch bản demo; đánh dấu từng tiêu chí nghiệm thu đạt hay chưa; ghi số đo mới vào `EVAL_RESULTS.md` |
| Retrospective | Ngay sau review, 15 phút | Một điều giữ, một điều đổi, một điều thử; tối đa một hành động cải tiến đưa vào sprint sau |

Theo dõi bằng GitHub Issues với nhãn epic và ưu tiên là đủ; ID trong tài liệu này dùng làm tiêu đề issue.

### Cập nhật backlog theo thực tế

Sau mỗi review:

1. Mục chưa đạt đủ tiêu chí quay lại backlog với ước lượng phần còn lại; không tính điểm một phần.
2. Tốc độ của sprint vừa xong là mức xếp cho sprint kế tiếp.
3. Kết luận của spike được viết thành mục backlog cụ thể, có tiêu chí nghiệm thu.
4. Lỗi và điểm yếu lộ ra từ số đo đánh giá trở thành mục backlog mới, xếp ưu tiên cùng các mục khác.
5. Cập nhật bảng đối chiếu trong `PROJECT_STATUS.md` cho các yêu cầu vừa đổi trạng thái.
6. Chỉ lên chi tiết task cho sprint kế tiếp; các sprint xa hơn giữ ở mức mục tiêu.

## 6. Đánh giá AI

### Chuẩn bị dữ liệu

Hai tập, dùng cho hai mục đích khác nhau:

- **Tập tổng hợp (VOC-02).** Sinh từ mẫu câu, nhãn có sẵn theo cách sinh. Dùng để kiểm thử pipeline, đo lọt PII (nhờ bảng kê) và đánh giá hotspot (nhờ điểm nóng cài sẵn). Không dùng để kết luận về chất lượng phân loại.
- **Tập gán nhãn tay (VOC-70).** Phản hồi tiếng Việt về bất động sản, ưu tiên lấy từ dữ liệu thật đã ẩn danh; nếu chưa có thì tự viết theo văn phong thật. Phải có ca khó: một phản hồi nhiều khía cạnh, mỉa mai, viết không dấu, teencode, khen và chê lẫn nhau, câu hỏi thuần túy. Có hướng dẫn gán nhãn một trang; 50 mẫu gán hai lượt để đo độ đồng thuận; tách dev để chỉnh prompt và test chỉ để báo cáo.

Baseline là prompt và model hiện tại chạy qua lệnh `evaluate`. Mỗi kết quả ghi kèm ngày, model, mã băm prompt và phiên bản tập đánh giá trong `docs/EVAL_RESULTS.md`. Chỉ cần một script và file JSON kết quả, không cần framework đánh giá riêng.

### Chỉ số

Cột "Ngưỡng" là **đề xuất để thảo luận**, chưa được thống nhất. Cột "Đã đo" chỉ ghi những gì thực sự đã chạy.

| Khía cạnh | Chỉ số đề xuất | Cách đo | Ngưỡng đề xuất, cần thống nhất | Đã đo |
| --- | --- | --- | --- | --- |
| Chủ đề | Macro-F1; precision, recall, F1 từng lớp; ma trận nhầm lẫn | Lệnh `evaluate` trên tập test gán nhãn tay | Macro-F1 ≥ 0,85; không lớp nào dưới 0,75 | 9/9 khớp trên dữ liệu mẫu tự viết. Không đại diện |
| Cảm xúc | Macro-F1; recall lớp tiêu cực (bỏ sót phàn nàn là lỗi đắt nhất) | Như trên | Macro-F1 ≥ 0,85; recall tiêu cực ≥ 0,90 | 9/9 khớp trên dữ liệu mẫu. Không đại diện |
| Bằng chứng | Tỷ lệ output bị loại vì bằng chứng rỗng hoặc không có trong văn bản | Đếm trong `errors` của báo cáo | ≤ 2% | 0/9 trong một lượt chạy thật |
| Gom cụm | ARI hoặc NMI so với nhãn vấn đề chi tiết; điểm mạch lạc do người chấm trên mẫu cụm | Script trên tập con có nhãn; soát tay 20 cụm, mỗi cụm 5 phản hồi | Đặt sau spike VOC-22 | Chưa đo |
| Hotspot | Recall trên điểm nóng cài sẵn; tỷ lệ báo nhầm trên chuỗi ổn định; số ngày trễ | Sinh nhiều chuỗi tổng hợp với seed khác nhau | Recall ≥ 0,90; báo nhầm ≤ 5% số tổ hợp dự án–chủ đề–tuần | Chưa đo |
| Tính có căn cứ | Tỷ lệ con số trong báo cáo khớp thống kê; tỷ lệ nhận định có ID hợp lệ; tỷ lệ nhận định diễn giải đúng (người chấm) | Bộ kiểm tra tự động của VOC-42; soát tay 20 nhận định | Số liệu 100% vì bản sai bị loại; ID hợp lệ 100%; diễn giải đúng ≥ 90% | Một bản nháp, so bằng mắt, khớp. Chưa phải phép đo |
| Lọt PII | Tỷ lệ lọt theo loại định danh; tỷ lệ che nhầm | Lệnh `pii-check` với bảng kê; bộ ca khó viết tay | Email, số điện thoại, số giấy tờ: 0 lọt trên tập kiểm tra; tên người: recall ≥ 0,95 | 8/9 ca thử định tính bị lọt. Chưa có tỷ lệ |
| Độ trễ | p50, p95 mỗi phản hồi; thời gian xử lý N phản hồi; thời gian tạo báo cáo | Từ thông tin lượt chạy (VOC-20) | Đặt sau khi có số đo Sprint 1 | Một lời gọi 1,86 giây; 9 phản hồi khoảng 16 giây. Quan sát lẻ |
| Chi phí | Token vào và ra mỗi phản hồi, mỗi báo cáo; chi phí trên 1.000 phản hồi; tỷ trọng lời gọi model lớn | Token từ thông tin lượt chạy nhân đơn giá khai báo trong cấu hình | Đặt sau khi có số đo Sprint 1 | Một lời gọi: 248 token vào, 37 token ra. Chưa có chi phí |

Hai lưu ý khi dùng các chỉ số này:

- Ngưỡng 0 lọt cho số điện thoại và email chỉ có nghĩa trên tập kiểm tra đã biết; nó không chứng minh dữ liệu thật an toàn tuyệt đối, nên cần bổ sung ca khó mỗi khi phát hiện dạng mới.
- Bộ kiểm tra số liệu bắt được con số sai, không bắt được diễn giải sai (ví dụ gọi một mức tăng nhỏ là "nghiêm trọng"). Phần đó cần người soát, và cũng là lý do HITL là bắt buộc.
