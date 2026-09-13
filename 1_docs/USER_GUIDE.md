# Cẩm nang Hướng dẫn Sử dụng AutoForm (User & Operation Guide)

> **Mã tài liệu**: GUID-001  
> **Phiên bản**: 1.0.0  
> **Dành cho**: Người dùng cuối & Nhà phát triển  

---

## 📌 1. Giới thiệu tổng quan

**AutoForm** là công cụ hỗ trợ tự động điền biểu mẫu trực tuyến thông minh. Thay vì phải gõ lại họ tên, email, số điện thoại, trường đại học hay số năm kinh nghiệm một cách thủ công, AutoForm giúp bạn tự động phân tích trang web form, ghép nối các câu hỏi với thông tin cá nhân và điền chính xác vào trình duyệt chỉ trong vài giây.

Hệ thống tuân thủ quy trình **Human-in-the-Loop** 5 bước an toàn:
```text
  [1. Phân tích Form] ──> [2. Ánh xạ dữ liệu] ──> [3. Người dùng duyệt] ──> [4. Điền Form] ──> [5. Nộp Form]
```

---

## 🛠️ 2. Hướng dẫn cài đặt từng bước (Installation)

### Yêu cầu hệ thống
- Hệ điều hành: Windows, macOS, hoặc Linux.
- Python: Phiên bản **3.11** hoặc cao hơn.

### Các bước cài đặt:

```bash
# Bước 1: Clone kho lưu trữ dự án
git clone https://github.com/tuanpanh05/autoForm-tool.git
cd autoForm-tool

# Bước 2: Tạo và kích hoạt môi trường ảo Python (Virtual Environment)
python -m venv .venv

# Kích hoạt trên Windows (PowerShell / CMD):
.venv\Scripts\activate

# Kích hoạt trên Linux / macOS:
# source .venv/bin/activate

# Bước 3: Cài đặt gói ứng dụng và các thư viện phụ thuộc
pip install -e ".[dev]"

# Bước 4: Cài đặt trình duyệt Playwright Chromium
playwright install chromium
```

---

## 👤 3. Quản lý Hồ sơ người dùng (User Profile Management)

Hồ sơ người dùng (Profile) là nơi chứa các thông tin cá nhân của bạn để tool sử dụng điền form. Dữ liệu này được lưu hoàn toàn cục bộ dưới dạng file JSON tại thư mục `~/.autoform/profiles/`.

### 3.1 Cấu trúc thông tin trong Profile

Một Profile tiêu chuẩn gồm các nhóm thông tin sau:
- **Cá nhân (`personal`)**: `full_name`, `first_name`, `last_name`, `date_of_birth`, `gender`
- **Liên hệ (`contact`)**: `email`, `phone`, `address`
- **Học vấn (`education`)**: `university`, `major`, `gpa`, `graduation_year`
- **Công việc (`work`)**: `company`, `position`, `years_of_experience`
- **Kỹ năng (`skills`)**: `programming_languages`, `tools`
- **Tùy chỉnh (`custom`)**: `github`, `linkedin`, `portfolio`

---

### 3.2 Các lệnh thao tác Profile qua CLI

#### 1. Xem danh sách các Profile hiện có:
```bash
autoform profiles list
```

#### 2. Xem chi tiết thông tin của 1 Profile (Ví dụ xem profile `default`):
```bash
autoform profiles show default
```

#### 3. Tạo Profile mới bằng trình tương tác câu hỏi:
```bash
autoform profiles create john_doe
```
*Hệ thống sẽ hỏi từng thông tin một, bạn chỉ cần nhập vào và ấn Enter (nhấn Enter trực tiếp để bỏ qua trường không bắt buộc).*

#### 4. Cập nhật 1 trường dữ liệu cụ thể trong Profile:
```bash
# Cú pháp: autoform profiles update <tên_profile> <đường_dẫn_trường> <giá_trị_mới>
autoform profiles update default contact.email new_email@example.com
```

---

## 🚀 4. Hướng dẫn Tự động điền Form (Filling Form Guide)

AutoForm hỗ trợ 2 chế độ vận hành linh hoạt:

---

### Chế độ 1: Giao diện Menu tương tác Rich CLI (Khuyên dùng cho người mới)

Chạy câu lệnh chính của ứng dụng:
```bash
python -m autoform
```

Giao diện Rich Terminal hiển thị Menu chính:
```text
  [1]  Fill Form        Auto-fill a web form
  [2]  Profile          Manage your user profile
  [3]  Settings         Configure AutoForm
  [0]  Exit             Exit AutoForm
```

#### Quy trình sử dụng Chế độ 1:

1. Nhập số `1` và ấn Enter.
2. **Nhập URL của Form**: Dán đường dẫn trang web Form (HTML tiêu chuẩn hoặc Google Forms).
3. **Xem Bảng ánh xạ kết quả (Mapping Table)**:
   - Tool tự động bật trình duyệt ngầm, phân tích tất cả các trường và hiển thị bảng ghép nối kèm điểm tin cậy:
     - 🟢 **HIGH (>= 85%)**: Khớp chính xác tuyệt đối.
     - 🟡 **MEDIUM (60-84%)**: Khớp tương đối, cần kiểm tra.
     - 🔴 **LOW (30-59%)**: Độ tin cậy thấp.
4. **Phê duyệt kết quả (Review)**:
   - Gõ `a` (Accept all): Phê duyệt tự động tất cả các trường độ tin cậy `HIGH`.
   - Gõ `r` (Review): Duyệt thủ công từng trường một (gõ `y` để duyệt, `n` để từ chối).
   - Gõ `q` (Quit): Hủy bỏ.
5. **Thực thi điền Form (Fill)**:
   - Xác nhận `Y` để tool tự động gõ dữ liệu vào trình duyệt.
6. **Xác nhận Nộp Form (Submit)**:
   - Tool sẽ hỏi bạn có muốn nhấn nút Submit không (`y/n`).
   - Nếu chọn `n`, trình duyệt giữ nguyên trang đã điền dữ liệu để bạn tự kiểm tra lại trước khi nhấn nộp thủ công.

---

### Chế độ 2: Lệnh thực thi nhanh trực tiếp (Direct CLI Command)

Bạn có thể truyền trực tiếp URL và tên Profile qua lệnh:

```bash
autoform fill-form "https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform" --profile default
```

---

## ❓ 5. Các câu hỏi thường gặp & Xử lý sự cố (FAQ & Troubleshooting)

### Q1: Tool có điền được các Form có nhiều trang (Multi-page Forms) không?
> **Trả lời**: Có. Với Google Forms hoặc Form HTML có nhiều trang, sau khi điền xong trang 1, tool sẽ nhận diện nút "Tiếp" (`Next`) và hỗ trợ bạn chuyển tiếp sang trang 2.

### Q2: Nếu Form dính CAPTCHA thì xử lý thế nào?
> **Trả lời**: AutoForm tuân thủ nguyên tắc an toàn. Khi quét thấy iframe reCAPTCHA hoặc hCaptcha, tool sẽ tự động phát hiện, tạm ngưng thao tác Submit và thông báo trên terminal để bạn tự tích giải CAPTCHA trên trình duyệt.

### Q3: Làm sao để mở ẩn/hiện cửa sổ Trình duyệt khi tool chạy?
> **Trả lời**: Bạn có thể tùy chỉnh trong file `.env` hoặc `4_configs/default.toml`:
> - `BROWSER_HEADLESS=false`: Trình duyệt hiển thị trực quan (Mặc định).
> - `BROWSER_HEADLESS=true`: Trình duyệt chạy ẩn ngầm dưới nền.

### Q4: Mật khẩu hay Thẻ ngân hàng của tôi có bị tool lưu lại không?
> **Trả lời**: **KHÔNG BAO GIỜ**. AutoForm tích hợp bộ lọc an toàn `Sensitive Auto-Exclusion`. Các trường có kiểu Mật khẩu (`type="password"`), Thẻ tín dụng, CVV, OTP sẽ tự động bị loại trừ và không bao giờ được lưu trữ hay điền tự động.
