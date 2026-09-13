# Đặc tả Thiết kế Kỹ thuật Chi tiết AutoForm (Technical Design Specification)

> **Mã tài liệu**: TECH-001  
> **Trạng thái**: Đã duyệt (Approved)  
> **Phiên bản**: 1.0.0  

---

## 1. Tổng quan Thiết kế

Tài liệu này quy định đặc tả kỹ thuật chi tiết về cấu trúc dữ liệu, giao diện lập trình (API Interface), thuật toán xử lý và quy trình phối hợp giữa các Module trong hệ thống AutoForm.

---

## 2. Đặc tả Mô hình Dữ liệu (Domain Data Models)

### 2.1 FormField (`autoform.domain.models.FormField`)
Biểu diễn thông tin chi tiết của một trường dữ liệu trích xuất từ Form:
- `field_id: str`: Định danh duy nhất của trường trong Form.
- `label: str`: Nhãn/Câu hỏi của trường thu thập được từ trang Web.
- `label_source: LabelSource`: Nguồn trích xuất nhãn (ví dụ: `LABEL_FOR`, `ARIA_LABEL`, `QUESTION_TEXT`).
- `field_type: FieldType`: Loại trường dữ liệu (`TEXT`, `EMAIL`, `RADIO`, `CHECKBOX`, `SELECT`, v.v.).
- `required: bool`: Đánh dấu trường có bắt buộc điền hay không.
- `options: list[FieldOption]`: Danh sách các lựa chọn (dành cho Radio, Checkbox, Select).
- `locator: str`: CSS Selector hoặc XPath để định vị phần tử trên trình duyệt.
- `validation: FieldValidation`: Các ràng buộc kỹ thuật (min/max length, pattern regex).

### 2.2 UserProfile (`autoform.domain.models.UserProfile`)
Biểu diễn thông tin hồ sơ lưu trữ của người dùng theo cấu trúc nhóm:
- `personal: dict[str, Any]`: Thông tin cá nhân (họ tên, ngày sinh, giới tính).
- `contact: dict[str, Any]`: Thông tin liên hệ (email, số điện thoại, địa chỉ).
- `education: dict[str, Any]`: Thông tin học vấn (trường đại học, chuyên ngành, GPA).
- `work: dict[str, Any]`: Thông tin công việc (công ty, vị trí, số năm kinh nghiệm).
- `skills: dict[str, Any]`: Kỹ năng (ngôn ngữ lập trình, công cụ).
- `custom: dict[str, Any]`: Các trường tùy chỉnh tự định nghĩa (links GitHub, LinkedIn).

### 2.3 FieldMapping (`autoform.domain.models.FieldMapping`)
Biểu diễn kết quả ánh xạ giữa một trường trên Form với thông tin trong Profile:
- `form_field: FormField`: Trường trên Form cần điền.
- `profile_path: str`: Đường dẫn đến trường dữ liệu tương ứng trong Profile (ví dụ: `personal.full_name`).
- `value: Any`: Giá trị dữ liệu sẽ được điền vào Form.
- `confidence: float`: Điểm số tin cậy (từ `0.0` đến `1.0`).
- `confidence_level: ConfidenceLevel`: Cấp độ tin cậy (`HIGH`, `MEDIUM`, `LOW`, `NO_MATCH`).
- `approved: bool`: Trạng thái đã được người dùng phê duyệt hay chưa.

---

## 3. Thuật toán trích xuất Label 9 tầng (9-Level Label Extraction)

Khi phân tích Form HTML tiêu chuẩn (`GenericHTMLFormAdapter`), hệ thống duyệt tìm nhãn của phần tử theo thứ tự ưu tiên giảm dần:

1. **Explicit `<label for="id">`**: Tìm thẻ `<label>` có thuộc tính `for` trỏ đúng `id` của input.
2. **`aria-label`**: Lấy giá trị trực tiếp từ thuộc tính `aria-label`.
3. **`aria-labelledby`**: Tìm phần tử tham chiếu theo `id` ghi trong `aria-labelledby`.
4. **Wrapping `<label>`**: Trường hợp phần tử input nằm bên trong thẻ `<label>`.
5. **`placeholder`**: Sử dụng gợi ý nhập liệu làm nhãn thay thế.
6. **`title` attribute**: Thuộc tính `title` của phần tử.
7. **Nearby Text**: Văn bản nằm ở các phần tử liền trước (`<p>`, `<span>`, `<div>`, `<label>`).
8. **`name` attribute**: Thuộc tính `name` của input (được làm sạch qua thuật toán `_humanize`).
9. **`id` attribute**: Thuộc tính `id` của input (được làm sạch qua thuật toán `_humanize`).

---

## 4. Đặc tả Động cơ Ánh xạ (Mapping Engine Pipeline)

```text
Input: FormField + UserProfile
   |
   +---> 1. Chạy RuleMatcher (Exact & Alias Match) ---> Kết quả điểm R
   |
   +---> 2. Chạy FuzzyMatcher (RapidFuzz Ratio)    ---> Kết quả điểm F
   |
   +---> 3. Lựa chọn Match có điểm cao nhất
   |
   +---> 4. ConfidenceScorer:
   |        - Cộng thưởng nếu khớp loại trường (+0.05 ~ +0.10)
   |        - Trừ phạt nếu lệch loại trường (-0.20 ~ -0.40)
   |        - Cộng thưởng ngữ cảnh Section (+0.05)
   |        - Giới hạn điểm [0.0, 1.0]
   |
   +---> 5. Phân loại ConfidenceLevel (HIGH >= 0.85, MEDIUM >= 0.60, LOW >= 0.30)
   |
Output: FieldMapping (mặc định approved = False)
```

---

## 5. Xử lý an toàn & Trường nhạy cảm (Safety Safeguards)

1. **Auto-Exclusion**: Các trường có `field_type` là `PASSWORD` hoặc `HIDDEN` tự động bị loại trừ khỏi luồng điền.
2. **Sensitive Keyword Detection**: Các trường có nhãn chứa từ khóa nhạy cảm (`credit card`, `cvv`, `ssn`, `mật khẩu`, `pin`) sẽ bị loại bỏ khỏi danh sách ánh xạ.
3. **CAPTCHA Guard**: Trước khi nhấn nút Submit, `AutofillEngine` quét trang để phát hiện các iframe CAPTCHA. Nếu có, hệ thống ngừng gửi lệnh submit và cảnh báo cho người dùng.
4. **Human Delay Simulation**: Mỗi thao tác `fill()`, `click()`, `check()` được chèn thêm khoảng trễ ngẫu nhiên ngẫu nhiên trong khoảng cấu hình (`100ms - 300ms`).
