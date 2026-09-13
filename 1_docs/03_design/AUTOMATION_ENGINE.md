# Đặc tả Động cơ Tự động điền Form (Autofill Engine Specification)

> **Mã tài liệu**: DES-AUTO-001  
> **Trạng thái**: Đã duyệt (Approved)  

Tài liệu này quy định chi tiết về cơ chế vận hành, chiến lược điền từng loại trường và thuật toán giả lập hành vi con người của `AutofillEngine`.

---

## 1. Luồng vận hành của AutofillEngine

```text
Danh sách FieldMapping (đã duyệt approved = True)
                        |
                        v
          +---------------------------+
          |  Kiểm tra an toàn (Safety) | ---> Bỏ qua Password / CC / Sensitive
          +---------------------------+
                        |
                        v
          +---------------------------+
          | Quét kiểm tra CAPTCHA     | ---> Cảnh báo & Tạm dừng nếu có CAPTCHA
          +---------------------------+
                        |
                        v
          +---------------------------+
          | Vòng lặp điền các trường  |
          |  - Chọn chiến lược theo   |
          |    FieldType              |
          |  - Chèn khoảng trễ ngẫu   |
          |    nhiên (Random Delay)   |
          +---------------------------+
                        |
                        v
                  FillResult (Success, Failed, Skipped)
```

---

## 2. Chiến lược điền theo loại trường (Field Filling Strategies)

### 2.1 Văn bản (Text, Email, Tel, Number, Url, Date, Textarea)
- Gọi phương thức `browser.fill(locator, str(value))`.
- Xóa sạch dữ liệu cũ trước khi gõ văn bản mới.

### 2.2 Nút chọn Radio (`FieldType.RADIO`)
- Duyệt qua danh sách `options` của trường.
- So sánh chuỗi `value` hoặc `text` của option với giá trị cần điền (không phân biệt chữ hoa/thường).
- Gọi phương thức `browser.click(option.locator)`.

### 2.3 Hộp kiểm Checkbox (`FieldType.CHECKBOX`)
- Hỗ trợ cả trường hợp giá trị đơn hoặc mảng danh sách giá trị (`list[str]`).
- Với mỗi giá trị cần chọn, tìm option tương ứng và gọi `browser.check(option.locator)`.

### 2.4 Danh sách thả xuống Select (`FieldType.SELECT`)
- Với HTML chuẩn: Gọi `browser.select_option(locator, value=str(value))`.
- Với Google Forms Dropdown (Listbox):
  1. Nhấp chuột vào phần tử Dropdown để mở danh sách tùy chọn.
  2. Tạm dừng `500ms` đợi danh sách hiển thị.
  3. Thực thi JavaScript click vào phần tử `[role="option"]` có nội dung khớp với giá trị cần chọn.

---

## 3. Thuật toán giả lập độ trễ người dùng (Human-like Delays)

Để tránh bị hệ thống chặn do phát hiện tự động hóa (Bot Detection), `AutofillEngine` ngẫu nhiên hóa độ trễ theo phân phối ngẫu nhiên:

$$\text{delay} = \text{random.uniform}(\text{min\_delay}, \text{max\_delay})$$

- **Độ trễ giữa các trường (Field Delay)**: Mặc định `100ms – 300ms`.
- **Độ trễ nhấp chuột (Click Delay)**: Mặc định `200ms – 500ms`.
- **Độ trễ trước khi Submit (Submit Delay)**: Mặc định `1000ms`.
