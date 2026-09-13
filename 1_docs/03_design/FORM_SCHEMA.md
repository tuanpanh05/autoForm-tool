# Đặc tả Schema Form & Mô hình biểu diễn trường (Form Schema Specification)

> **Mã tài liệu**: DES-FORM-001  
> **Trạng thái**: Đã duyệt (Approved)  

Tài liệu này quy định chi tiết cấu trúc Schema biểu diễn biểu mẫu và mô hình hóa các trường thông tin trong AutoForm.

---

## 1. Mô hình FormSchema

`FormSchema` là cấu trúc tổng thể đại diện cho toàn bộ biểu mẫu trực tuyến sau khi được phân tích.

```json
{
  "form_id": "form_1726200000",
  "url": "https://docs.google.com/forms/d/e/...",
  "title": "Biểu mẫu đăng ký thông tin cá nhân",
  "platform": "google_forms",
  "sections": [
    {
      "section_id": "section_0",
      "title": "Thông tin liên hệ",
      "order": 0,
      "fields": [ ... ]
    }
  ],
  "submit_locator": "div[role='button']:has-text('Gửi')",
  "has_captcha": false
}
```

---

## 2. Phân loại loại trường dữ liệu (FieldType Enum)

| Enum Value | Mã HTML tương ứng | Mô tả & Cách điền |
|---|---|---|
| `TEXT` | `<input type="text">` | Nhập văn bản một dòng |
| `EMAIL` | `<input type="email">` | Nhập địa chỉ email |
| `TEL` | `<input type="tel">` | Nhập số điện thoại |
| `NUMBER` | `<input type="number">` | Nhập giá trị số |
| `URL` | `<input type="url">` | Nhập đường dẫn trang web |
| `DATE` | `<input type="date">` | Nhập ngày tháng (YYYY-MM-DD) |
| `DATETIME` | `<input type="datetime-local">` | Nhập ngày giờ |
| `TEXTAREA` | `<textarea>` | Nhập văn bản nhiều dòng |
| `RADIO` | `<input type="radio">` / `[role="radio"]` | Chọn 1 trong danh sách lựa chọn |
| `CHECKBOX` | `<input type="checkbox">` / `[role="checkbox"]` | Chọn một hoặc nhiều lựa chọn |
| `SELECT` | `<select>` / `[role="listbox"]` | Chọn từ danh sách thả xuống |
| `PASSWORD` | `<input type="password">` | Trường mật khẩu (Tự động bỏ qua) |
| `HIDDEN` | `<input type="hidden">` | Trường ẩn (Tự động bỏ qua) |

---

## 3. Nguồn trích xuất Nhãn (LabelSource Enum)

Mỗi trường dữ liệu được gán nhãn kèm theo nguồn trích xuất để đánh giá mức độ tin cậy của nhãn:

- `LABEL_FOR`: Trích xuất từ thẻ `<label for="...">` chính thức.
- `ARIA_LABEL`: Trích xuất từ thuộc tính `aria-label`.
- `ARIA_LABELLEDBY`: Trích xuất từ phần tử tham chiếu `aria-labelledby`.
- `WRAPPING_LABEL`: Trích xuất từ thẻ `<label>` bao bọc bên ngoài.
- `QUESTION_TEXT`: Trích xuất từ phần tử câu hỏi của Google Forms.
- `PLACEHOLDER`: Trích xuất từ gợi ý `placeholder`.
- `NEARBY_TEXT`: Trích xuất từ văn bản nằm liền kề.
- `NAME_ATTRIBUTE`: Trích xuất và làm sạch từ thuộc tính `name`.
- `ID_ATTRIBUTE`: Trích xuất và làm sạch từ thuộc tính `id`.
