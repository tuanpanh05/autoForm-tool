# Đặc tả yêu cầu phần mềm AutoForm (Requirements Specification)

> **Mã tài liệu**: REQ-001  
> **Trạng thái**: Đã duyệt (Approved)  
> **Phiên bản**: 1.0.0  

---

## 1. Tổng quan hệ thống

AutoForm là một hệ thống ứng dụng Python cho phép tự động điền các biểu mẫu trực tuyến (Web Forms) dựa trên thông tin hồ sơ lưu trữ cá nhân (User Profile). Hệ thống áp dụng quy trình làm việc có cấu trúc: **Phân tích (Analyze) → Ánh xạ (Map) → Duyệt (Review) → Điền (Fill) → Nộp (Submit)**.

---

## 2. Yêu cầu chức năng (Functional Requirements)

### FR-1: Phân tích Form (Form Analysis)
- **FR-1.1**: Hệ thống phải hỗ trợ phân tích bất kỳ trang web biểu mẫu HTML tiêu chuẩn nào (`<form>`, `<input>`, `<textarea>`, `<select>`).
- **FR-1.2**: Hệ thống phải hỗ trợ phân tích biểu mẫu Google Forms (DOM div-based, ARIA roles, `data-params`).
- **FR-1.3**: Hệ thống phải áp dụng thuật toán tìm kiếm nhãn 9 tầng để trích xuất câu hỏi/nhãn của từng trường dữ liệu.
- **FR-1.4**: Hệ thống phải tự động phân loại loại trường (`TEXT`, `EMAIL`, `TEL`, `NUMBER`, `DATE`, `RADIO`, `CHECKBOX`, `SELECT`, `TEXTAREA`, `PASSWORD`, `HIDDEN`).
- **FR-1.5**: Hệ thống phải xác định được các ràng buộc kỹ thuật của trường (Bắt buộc, Độ dài tối đa/tối thiểu, Giá trị số min/max).

### FR-2: Ánh xạ trường thông minh (Semantic Field Mapping)
- **FR-2.1**: Hệ thống phải sử dụng thuật toán ghép nối dựa trên quy tắc (Rule-based Matcher) hỗ trợ từ đồng nghĩa cả tiếng Anh lẫn tiếng Việt (ví dụ: "Họ và tên" → `personal.full_name`).
- **FR-2.2**: Hệ thống phải áp dụng thuật toán chuỗi mờ (Fuzzy Matcher) với ngưỡng điểm tin cậy có thể cấu hình.
- **FR-2.3**: Hệ thống phải tính toán điểm tin cậy (Confidence Score từ `0.0` đến `1.0`) và phân loại điểm thành 4 cấp độ: `HIGH` (🟢 >= 85%), `MEDIUM` (🟡 60-84%), `LOW` (🔴 30-59%), `NO_MATCH` (⚪ < 30%).
- **FR-2.4**: Hệ thống phải tự động loại trừ các trường ẩn (`HIDDEN`) hoặc các trường đã có sẵn giá trị mặc định khỏi quá trình ánh xạ.

### FR-3: Phê duyệt từ người dùng (Human-in-the-Loop Review)
- **FR-3.1**: Hệ thống phải hiển thị bảng kết quả ánh xạ có mã màu tương ứng với từng cấp độ tin cậy.
- **FR-3.2**: Hệ thống phải cho phép người dùng phê duyệt nhanh tự động tất cả các trường có độ tin cậy cao (`HIGH`).
- **FR-3.3**: Hệ thống phải hỗ trợ giao diện xem và phê duyệt từng trường riêng biệt.
- **FR-3.4**: Chỉ những trường được người dùng phê duyệt (`approved = True`) mới được phép gửi tới Engine tự động điền.

### FR-4: Tự động điền Form (Autofill Engine)
- **FR-4.1**: Engine tự động điền phải thực thi chính xác các thao tác nhập liệu tương ứng với loại trường (gõ văn bản, chọn radio/checkbox, chọn dropdown list).
- **FR-4.2**: Hệ thống phải giả lập hành vi gõ bàn phím và nhấp chuột của con người bằng các khoảng trễ ngẫu nhiên (Random Delays).
- **FR-4.3**: Hệ thống phải tự động phát hiện CAPTCHA (reCAPTCHA, hCaptcha) và tạm dừng để thông báo cho người dùng xử lý.
- **FR-4.4**: Hệ thống chỉ thực hiện hành động Gửi Form (`Submit`) khi có xác nhận đồng ý trực tiếp từ người dùng.

### FR-5: Quản lý Hồ sơ người dùng (User Profile Storage)
- **FR-5.1**: Hệ thống phải lưu trữ hồ sơ dưới dạng file JSON cấu trúc đặt tại thư mục cục bộ (`~/.autoform/profiles/`).
- **FR-5.2**: Hệ thống phải hỗ trợ truy vết trường dữ liệu theo đường dẫn phân cấp (ví dụ: `personal.full_name`, `contact.email`).
- **FR-5.3**: Cung cấp giao diện CLI quản lý profile: Xem, Tạo mới, Chỉnh sửa trường, Liệt kê danh sách và Xóa profile.

---

## 3. Yêu cầu phi chức năng (Non-Functional Requirements)

### NFR-1: Hiệu năng (Performance)
- **NFR-1.1**: Thời gian phân tích trang form HTML tiêu chuẩn không quá **3 giây**.
- **NFR-1.2**: Thời gian tính toán ghép nối dữ liệu cho toàn bộ form không quá **500ms**.
- **NFR-1.3**: Tốc độ phản hồi của CLI Terminal không quá **100ms** cho mỗi thao tác tương tác.

### NFR-2: Bảo mật & Quyền riêng tư (Security & Privacy)
- **NFR-2.1**: Dữ liệu hồ sơ cá nhân chỉ được lưu trữ cục bộ trên máy tính người dùng (Local-First), không tự động tải lên Server/Cloud.
- **NFR-2.2**: Các trường dữ liệu nhạy cảm (Mật khẩu, Thẻ tín dụng, Số CMND/CCCD) KHÔNG BAO GIỜ được tự động lưu trữ hoặc tự động điền.
- **NFR-2.3**: Tất cả các thông tin định danh cá nhân (PII: Email, SĐT, Token) trong dữ liệu log phải được che giấu (`[REDACTED]`).

### NFR-3: Độ tin cậy & Ổn định (Reliability)
- **NFR-3.1**: Hệ thống phải đạt độ bao phủ kiểm thử (Test Coverage) tối thiểu **80%**.
- **NFR-3.2**: Hệ thống phải tự động xử lý các ngoại lệ (Exception Handling) khi trình duyệt mất kết nối hoặc selector không tồn tại mà không làm ngắt đột ngột ứng dụng.

---

## 4. Ràng buộc kỹ thuật (Technical Constraints)

- **Ngôn ngữ lập trình**: Python 3.11+.
- **Trình điều khiển trình duyệt**: Playwright Chromium / Firefox / Webkit.
- **Giao diện CLI**: Rich Terminal Framework.
- **Quản lý cấu hình**: TOML & `.env`.

---

## 5. Các tính năng nằm ngoài phạm vi MVP (Out of Scope)

- Tự động giải mã CAPTCHA bằng AI/Bypass.
- Tự động thanh toán thẻ ngân hàng.
- Tải file đính kèm tự động.
- Browser Extension (Extension Chrome/Firefox).
- Đồng bộ dữ liệu qua Cloud Storage.
