# Chính sách Bảo mật & Quyền riêng tư (Security & Privacy Specification)

> **Mã tài liệu**: SEC-001  
> **Trạng thái**: Đã duyệt (Approved)  

Tài liệu này quy định các tiêu chuẩn an toàn thông tin, bảo vệ quyền riêng tư và quy tắc che giấu dữ liệu PII trong AutoForm.

---

## 1. Nguyên tắc Bảo mật Cốt lõi (Core Security Principles)

### 1.1 Nguyên tắc Local-First Privacy
- Toàn bộ dữ liệu hồ sơ cá nhân (`UserProfile`) được lưu trữ hoàn toàn cục bộ trên máy tính của người dùng tại thư mục `~/.autoform/profiles/`.
- Không gửi bất kỳ dữ liệu cá nhân nào tới Server trung gian, Cloud hay bên thứ ba trong luồng vận hành tiêu chuẩn.

### 1.2 Nguyên tắc Loại trừ Trường Nhạy cảm (Sensitive Field Auto-Exclusion)
Hệ thống tự động bỏ qua và KHÔNG BAO GIỜ lưu trữ hay tự động điền các trường thuộc các nhóm sau:
1. **Trường Mật khẩu (`FieldType.PASSWORD`)**: Tất cả các ô nhập mật khẩu hoặc mã PIN.
2. **Thông tin Thẻ ngân hàng & Tài chính**: Thẻ tín dụng (`credit card`), CVV/CVC, Số tài khoản ngân hàng.
3. **Số định danh cá nhân nhạy cảm**: Số Bảo hiểm xã hội (SSN), Mật mã xác thực OTP.

---

## 2. Quy tắc Che giấu dữ liệu PII trong Logs (PII Redaction)

Mọi log sự kiện được ghi ra console hoặc file (`structlog`) đều phải trải qua bộ lọc `_redact_pii` để thay thế thông tin cá nhân bằng các nhãn an toàn:

| Loại dữ liệu | Biểu thức Regex kiểm tra | Chuỗi mã hóa thay thế |
|---|---|---|
| Địa chỉ Email | `[\w.+-]+@[\w-]+\.[\w.-]+` | `[EMAIL_REDACTED]` |
| Số điện thoại | `\b\d{10,11}\b` | `[PHONE_REDACTED]` |
| API Key (OpenAI / Anthropic) | `sk-[a-zA-Z0-9]{20,}` | `[API_KEY_REDACTED]` |
| Bearer Token | `Bearer\s+[a-zA-Z0-9._-]+` | `[BEARER_TOKEN_REDACTED]` |
| Từ khóa nhạy cảm | `password`, `secret`, `token`, `profile_value` | `[REDACTED]` |

---

## 3. An toàn Ngữ cảnh Trình duyệt (Browser Session Isolation)

- Mỗi phiên chạy tự động điền được thực thi trong một `BrowserContext` riêng biệt.
- Cookies, Cache và Session Data của trình duyệt được dọn dẹp sạch sẽ ngay sau khi người dùng đóng trình duyệt hoặc kết thúc lệnh fill form.
