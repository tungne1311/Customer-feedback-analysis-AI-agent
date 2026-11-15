# Kết quả đánh giá

Mỗi lần đo ghi một mục: ngày, model, mã băm prompt, bộ dữ liệu, ai gán nhãn, kết quả, giới hạn. Không xóa mục cũ, để so sánh được giữa các lần đổi prompt hoặc model.

## 2026-11-15 · Đánh giá Google Maps thật, nhãn do Claude gán và người dùng chấp nhận

### Thiết lập

| Mục | Giá trị |
| --- | --- |
| Model phân loại | `gemini-3.5-flash-lite`, thinking minimal |
| Mã băm prompt phân loại | `0273d97cd02c` (12 ký tự đầu SHA-256 của `CLASSIFY_INSTRUCTIONS`) |
| Bộ dữ liệu | 164 đánh giá Google Maps tiếng Việt của 3 khu đô thị đã bàn giao, cùng một chủ đầu tư (RealA 54, RealB 55, RealC 55; tên thật giữ ngoài repo), thu ngày 15/11/2026 bằng `E:\VoC-data-collector`. Đã lọc câu vô ích, ẩn danh tên người |
| Nhãn | **Do Claude gán nháp, người dùng chấp nhận cả bộ, chưa duyệt từng dòng.** Kết quả dưới đây đo mức đồng thuận giữa Gemini và nhãn của một model khác, không phải độ chính xác so với nhãn của người |
| Luật gán nhãn | `E:\VoC-data-collector\README.md`, mục "Luật gán nhãn" |
| Lệnh | `python -m src analyze --input E:\VoC-data-collector\output\real_feedback.json --output outputs\real_report.json` |

### Kết quả

163/164 phân tích thành công. Lỗi duy nhất là model trích bằng chứng không có trong câu gốc.

| Chỉ số | Giá trị | Ghi chú |
| --- | --- | --- |
| Độ chính xác chủ đề | 70,6% (115/163) | Kéo xuống chủ yếu do lệch định nghĩa `other` (xem dưới) |
| Macro-F1 chủ đề | 0,66 | Tính trên 5 lớp có mẫu. `legal_process` không có mẫu nào |
| Độ chính xác cảm xúc | 92,0% (150/163) | |
| Macro-F1 cảm xúc | 0,73 | `neutral` chỉ có 2 mẫu nên F1 lớp này không có ý nghĩa |
| Recall tiêu cực | 0,88 | 11 câu tiêu cực bị chấm trung tính hoặc tích cực |
| Thời gian | 382 giây cho lượt đầu và 136 giây cho lượt chạy lại 35 câu | Chưa đo token (chờ VOC-20) |

**Chủ đề theo từng lớp:**

| Lớp | Số mẫu | Precision | Recall | F1 |
| --- | --- | --- | --- | --- |
| price | 13 | 0,79 | 0,85 | 0,81 |
| construction_progress | 6 | 0,62 | 0,83 | 0,71 |
| amenities | 83 | 0,69 | 0,98 | 0,81 |
| legal_process | 0 | – | – | – |
| sales_service | 16 | 0,78 | 0,88 | 0,82 |
| other | 45 | 1,00 | 0,09 | 0,16 |

**Ma trận nhầm lẫn chủ đề** (hàng là nhãn, cột là dự đoán):

| | price | progress | amenities | legal | sales | other |
| --- | --- | --- | --- | --- | --- | --- |
| price | 11 | 0 | 2 | 0 | 0 | 0 |
| progress | 1 | 5 | 0 | 0 | 0 | 0 |
| amenities | 1 | 0 | 81 | 0 | 1 | 0 |
| sales | 0 | 0 | 2 | 0 | 14 | 0 |
| other | 1 | 3 | 33 | 1 | 3 | 4 |

### Phân tích lỗi

1. **33/45 câu gán `other` bị dự đoán là `amenities`.** Prompt định nghĩa amenities là "tiện ích, cơ sở vật chất", không nói gì về các khía cạnh còn lại, nên model xếp hạ tầng, quy hoạch, giao thông vào amenities. Đây là **lệch định nghĩa giữa prompt và luật gán nhãn**, không chỉ là lỗi của model. 45 câu `other` gồm:

   | Khía cạnh chính | Số câu |
   | --- | --- |
   | Vị trí, giao thông | 14 |
   | Quy hoạch, kiến trúc | 9 |
   | Vệ sinh, môi trường | 5 |
   | Hài lòng chung, không nêu khía cạnh | 5 |
   | Hạ tầng (ngập, thoát nước, sóng điện thoại) | 4 |
   | An ninh, ban quản lý | 3 |
   | Dân cư thưa | 3 |
   | Chất lượng công trình | 2 |

2. **9/13 lỗi cảm xúc là câu khen chê lẫn lộn.** Luật gán nhãn chọn ý chê, còn prompt không có luật này, nên model chấm trung tính hoặc tích cực. Những câu 4–5 sao có một lời chê là trường hợp hay gặp nhất.

3. **Gói miễn phí giới hạn 15 lời gọi/phút.** Lượt đầu có 35 câu lỗi 429 vì pipeline gọi tuần tự nhanh hơn mức này, còn retry mặc định (3 lần) chờ quá ngắn. Chạy lại 35 câu với `VOC_RETRY_ATTEMPTS=8` thì thành công hết.

### Giới hạn của lần đo này

- Nhãn không phải của người: xem dòng "Nhãn" ở bảng thiết lập.
- `legal_process` có 0 mẫu, `construction_progress` 6, `neutral` 2: **không kết luận được** về các lớp này.
- Ba dự án cùng một chủ đầu tư, đều đã bàn giao; nhiều đánh giá đến từ khách tham quan.
- Chỉ một lần chạy, chưa đo độ dao động giữa các lần chạy.
- 164 mẫu chưa tách dev/test. Nếu sửa prompt dựa trên chính bộ này rồi đo lại trên nó, kết quả sẽ lạc quan hơn thực tế.

### Việc nên làm tiếp

- **Quyết định Q6** (checklist Sprint 1) dựa trên bảng trên. Hai hướng:
  - Thêm chủ đề `location_infrastructure` (vị trí, giao thông, hạ tầng: 18 câu, 11% bộ dữ liệu).
  - Giữ 6 chủ đề nhưng viết rõ ranh giới `amenities`/`other` trong prompt.
- **Nếu sửa prompt:** thêm luật khen chê lẫn lộn và ranh giới chủ đề, tách bộ này thành dev/test, chỉ chỉnh prompt trên dev, rồi ghi kết quả test thành một mục mới ở file này.
- **Duyệt tay** ít nhất các câu khen chê lẫn lộn và các câu `other`, để nhãn đáng tin hơn trước khi dùng làm tập test.
- **Giới hạn tốc độ gọi** trong pipeline (đã thêm vào VOC-21).

## 2026-11-15 · Sau khi thêm chủ đề `location_infrastructure` (phương án A của Q6)

### Thiết lập

| Mục | Giá trị |
| --- | --- |
| Thay đổi so với mục trước | Thêm chủ đề `location_infrastructure`; prompt ghi ví dụ cho `amenities`, `location_infrastructure` và `other`. Phần cảm xúc của prompt không đổi |
| Model phân loại | `gemini-3.5-flash-lite`, thinking minimal |
| Mã băm prompt phân loại | `5cd84ba82a62` |
| Bộ dữ liệu | Cùng 164 đánh giá. 18 câu về vị trí, giao thông, hạ tầng được đổi nhãn từ `other` sang `location_infrastructure`; `other` còn 27 câu |
| Nhãn | Như mục trước: Claude gán, người dùng chấp nhận cả bộ, chưa duyệt từng dòng |
| Lệnh | `python -m src analyze --input E:\VoC-data-collector\output\real_feedback.json --output outputs\real_report_v2.json`, với `VOC_RETRY_ATTEMPTS=8` |

### Kết quả

163/164 phân tích thành công (cùng một câu lỗi bằng chứng như lần trước).

| Chỉ số | Trước | Sau |
| --- | --- | --- |
| Độ chính xác chủ đề | 70,6% (115/163) | **79,8% (130/163)** |
| Macro-F1 chủ đề (các lớp có mẫu) | 0,66 trên 5 lớp | **0,74 trên 6 lớp** |
| Độ chính xác cảm xúc | 92,0% | 92,6% |
| Recall tiêu cực | 0,88 | 0,88 |

**Chủ đề theo từng lớp:**

| Lớp | Số mẫu | Precision | Recall | F1 | F1 lần trước |
| --- | --- | --- | --- | --- | --- |
| price | 13 | 0,91 | 0,77 | 0,83 | 0,81 |
| construction_progress | 6 | 1,00 | 0,33 | 0,50 | 0,71 |
| amenities | 83 | 0,86 | 0,84 | 0,85 | 0,81 |
| location_infrastructure | 18 | 0,85 | 0,94 | 0,89 | (chưa có) |
| legal_process | 0 | – | – | – | – |
| sales_service | 16 | 1,00 | 0,56 | 0,72 | 0,82 |
| other | 27 | 0,55 | 0,81 | 0,66 | 0,16 |

**Ma trận nhầm lẫn chủ đề** (hàng là nhãn, cột là dự đoán):

| | price | progress | amenities | location | legal | sales | other |
| --- | --- | --- | --- | --- | --- | --- | --- |
| price | 10 | 0 | 3 | 0 | 0 | 0 | 0 |
| progress | 1 | 2 | 0 | 1 | 0 | 0 | 2 |
| amenities | 0 | 0 | 70 | 2 | 0 | 0 | 11 |
| location | 0 | 0 | 1 | 17 | 0 | 0 | 0 |
| sales | 0 | 0 | 2 | 0 | 0 | 9 | 5 |
| other | 0 | 0 | 5 | 0 | 0 | 0 | 22 |

### Nhận xét

1. **Chủ đề mới hoạt động đúng ý:** 17/18 câu vị trí và hạ tầng được xếp đúng. 27 câu `other` còn lại cũng được nhận ra tốt hơn nhiều: trước chỉ 2 câu đúng, nay 22 câu.
2. **Có tác dụng phụ: `other` hút bớt câu của lớp khác.** 11 câu `amenities`, 5 câu `sales_service` và 2 câu `construction_progress` nay bị xếp vào `other`. Recall của `sales_service` giảm từ 0,88 xuống 0,56. Nguyên nhân có khả năng nhất: ví dụ "an ninh" trong định nghĩa `other` của prompt mâu thuẫn với luật gán nhãn, vốn xếp thái độ của bảo vệ và ban quản lý vào `sales_service`. Chưa kiểm chứng từng câu.
3. **`construction_progress` giảm từ 5/6 xuống 2/6 câu đúng.** Với 6 mẫu thì chưa kết luận được đây là tác dụng phụ hay dao động.
4. **Mức dao động giữa hai lượt chạy:** phần cảm xúc của prompt không đổi, nhưng 8/162 câu (khoảng 5%) đổi kết quả cảm xúc. Chênh lệch dưới mức này giữa hai lượt chạy không nên coi là cải thiện hay suy giảm. Mức tăng 9 điểm của chủ đề lớn hơn mức dao động đó.

### Giới hạn

- Các giới hạn ở mục trước vẫn đúng.
- **Prompt được sửa dựa trên lỗi của chính 164 câu này rồi đo lại trên chúng**, nên mức tăng lạc quan hơn so với dữ liệu mới. Cần tách dev/test (VOC-70) trước lần chỉnh prompt tiếp theo.

### Việc nên làm tiếp

- Làm rõ trong prompt và luật gán nhãn: thái độ của bảo vệ, ban quản lý thuộc `sales_service` hay `other`. Gộp vào VOC-27, làm sau khi đã tách dev/test.
- Duyệt tay 18 câu bị `other` hút (11 `amenities`, 5 `sales_service`, 2 `construction_progress`) để biết lỗi ở model hay ở nhãn.

