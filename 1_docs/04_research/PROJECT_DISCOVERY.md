# Báo cáo Phân tích Bài toán & Nghiên cứu Khảo sát (Project Discovery)

> **Mã tài liệu**: RES-DISC-001  
> **Trạng thái**: Đã duyệt (Approved)  

Tài liệu này tổng hợp kết quả phân tích yêu cầu bài toán, chân dung người dùng mục tiêu và phân loại độ phức tạp của các loại Form trực tuyến.

---

## 1. Bài toán thực tế (Problem Statement)

Người dùng cá nhân, sinh viên, ứng viên xin việc và nhân viên văn phòng thường xuyên phải thực hiện công việc điền lại các thông tin lặp đi lặp lại (Họ tên, Ngày sinh, Email, SĐT, Trường học, Kinh nghiệm) trên hàng chục biểu mẫu trực tuyến khác nhau.
- **Rủi ro của các công cụ Autofill thông thường trên Trình duyệt**:
  - Nhầm lẫn giữa các trường có tên gần giống nhau (ví dụ: `First Name` vs `Full Name`, `Home Address` vs `Company Address`).
  - Không hỗ trợ các biểu mẫu sử dụng cấu trúc DOM tùy biến (như Google Forms, Typeform, Microsoft Forms).
  - Tự động điền dữ liệu nhạy cảm hoặc nộp Form ngoài ý muốn mà người dùng không kịp kiểm tra.

---

## 2. Phân loại độ phức tạp của Web Forms

| Cấp độ | Loại Form | Đặc điểm kỹ thuật | Giải pháp của AutoForm |
|---|---|---|---|
| **Cấp 1** | Standard HTML Form | Sử dụng `<form>`, `<input>`, `<label>`, `<select>` chuẩn | `GenericHTMLFormAdapter` + Thuật toán trích xuất Label 9 tầng |
| **Cấp 2** | Custom Widget Form | Sử dụng div custom radio/checkbox/dropdown | CSS selector theo thuộc tính ARIA role & `data-attributes` |
| **Cấp 3** | Google Forms | Không có thẻ `<form>`, câu hỏi bọc trong các thẻ `div` | `GoogleFormsAdapter` bóc tách theo `[data-params]` |
| **Cấp 4** | Multi-step / Multi-page | Form phân chia thành nhiều bước/trang tiếp theo | Nhận diện nút "Tiếp" (`Next`) và tự động chuyển trang |
| **Cấp 5** | Protected Form | Khóa bằng CAPTCHA hoặc Anti-bot | CAPTCHA Detection Guard + Giả lập độ trễ con người |

---

## 3. Chân dung người dùng mục tiêu (User Personas)

1. **Sinh viên / Ứng viên tuyển dụng**: Thường xuyên nộp hồ sơ ứng tuyển, đăng ký học bổng trên Google Forms và các trang tuyển dụng.
2. **Nhân viên Văn phòng / Marketer**: Cần thực hiện các khảo sát trực tuyến, đăng ký sự kiện.
3. **Lập trình viên / Tester**: Cần công cụ tự động hóa điền dữ liệu test mẫu nhanh chóng cho các dự án Web.
