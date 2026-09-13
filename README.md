# AutoForm — Công cụ tự động điền Form thông minh (Intelligent Form Auto-Fill Tool)

> **Phiên bản**: `v1.0.0` | **Trạng thái**: Sẵn sàng hoạt động (Đã pass 100% Tests)

Một ứng dụng Python thông minh hỗ trợ tự động điền các biểu mẫu trực tuyến (Web Forms), kết hợp trình điều khiển trình duyệt có cấu trúc (Browser Automation) với thuật toán ghép nối trường thông minh (Semantic Field Mapping).

---

## 📁 Cấu trúc thư mục dự án

```text
autoForm-tool/
├── 1_docs/                     # Tài liệu kiến trúc & thiết kế kỹ thuật (Tiếng Việt)
│   ├── 01_requirements/        # Yêu cầu & Đặc tả bài toán (REQUIREMENTS.md)
│   ├── 02_architecture/        # Kiến trúc hệ thống & Quyết định thiết kế (ARCHITECTURE.md, ADRs)
│   ├── 03_design/              # Chi tiết thiết kế các Module & Schema (TECHNICAL_DESIGN.md, v.v.)
│   ├── 04_research/            # Nghiên cứu bài toán & So sánh công nghệ (PROJECT_DISCOVERY.md, v.v.)
│   ├── 05_security/            # Chính sách bảo mật, Quyền riêng tư & Che giấu PII (SECURITY.md)
│   ├── 06_testing/             # Chiến lược kiểm thử & Đảm bảo chất lượng (TEST_STRATEGY.md)
│   ├── 07_ROADMAP.md           # Cột mốc phát triển & Tiến độ 12 Phase
│   └── INDEX.md                # Trang chỉ mục tổng hợp tài liệu
├── 2_src/autoform/             # Mã nguồn chính của ứng dụng Python Core
│   ├── cli/                    # Giao diện dòng lệnh Rich Terminal UI
│   ├── domain/                 # Models dữ liệu, Enums & Exception định nghĩa
│   ├── infrastructure/         # Cấu hình, Ghi log cấu trúc & Lưu trữ
│   ├── form_analyzer/          # Bộ phân tích Form & Adapters (Generic HTML, Google Forms)
│   ├── mapping/                # Engine khớp trường Rule-based & Fuzzy Matching
│   ├── automation/             # Engine tự động điền & Giả lập hành vi người dùng
│   ├── browser/                # Playwright Browser Adapter
│   ├── profile/                # Quản lý hồ sơ người dùng (CRUD Profile)
│   ├── validation/             # Bộ kiểm tra định dạng & ràng buộc dữ liệu
│   └── security/               # An toàn dữ liệu & Che giấu thông tin nhạy cảm
├── 3_tests/                    # Test suite kiểm thử tự động Pytest (93/93 Passed)
│   └── unit/                   # Unit tests cho models, matchers, adapters & validators
├── 4_configs/                  # Các file cấu hình mặc định & môi trường
└── 5_test_forms/               # Các mẫu biểu mẫu HTML phục vụ kiểm thử End-to-End
```

---

## 📖 1. Chỉ mục tài liệu (`1_docs/`)

Xem chi tiết tại [1_docs/INDEX.md](1_docs/INDEX.md):

1. **[Yêu cầu hệ thống](1_docs/01_requirements/REQUIREMENTS.md)** — Yêu cầu chức năng & phi chức năng
2. **[Kiến trúc hệ thống](1_docs/02_architecture/ARCHITECTURE.md)** — Sơ đồ kiến trúc & Các quyết định thiết kế (ADRs)
3. **[Thiết kế kỹ thuật](1_docs/03_design/TECHNICAL_DESIGN.md)** — Đặc tả chi tiết các Engine & Module
4. **[Nghiên cứu & Phân tích](1_docs/04_research/PROJECT_DISCOVERY.md)** — Phân tích loại form & So sánh công nghệ
5. **[Bảo mật & Quyền riêng tư](1_docs/05_security/SECURITY.md)** — Nguyên tắc Local-first & Redact dữ liệu PII
6. **[Chiến lược kiểm thử](1_docs/06_testing/TEST_STRATEGY.md)** — Kế hoạch test & Chuẩn mực kiểm thử
7. **[Lộ trình phát triển](1_docs/07_ROADMAP.md)** — Tiến độ chi tiết toàn bộ 12 Phase

---

## 🚀 2. Hướng dẫn khởi chạy nhanh

### Yêu cầu tiên quyết
- Python 3.11+
- Môi trường ảo virtualenv (`.venv`)

### Cài đặt môi trường

```bash
# 1. Clone repository
git clone <repo-url>
cd autoForm-tool

# 2. Tạo và kích hoạt môi trường ảo
python -m venv .venv
.venv\Scripts\activate      # Trên Windows
# source .venv/bin/activate # Trên Linux/macOS

# 3. Cài đặt các thư viện ở chế độ editable
pip install -e ".[dev]"

# 4. Cài đặt trình duyệt Playwright Chromium
playwright install chromium
```

### Các lệnh sử dụng

```bash
# Khởi chạy giao diện tương tác Rich Terminal (Analyze → Review → Fill → Submit)
python -m autoform

# Lệnh điền trực tiếp qua CLI
autoform fill-form "https://docs.google.com/forms/d/e/..." --profile default

# Quản lý hồ sơ người dùng (Profiles)
autoform profiles list
autoform profiles show default
```

---

## 🧪 3. Kiểm thử & Xác minh (`3_tests/`)

```bash
# Chạy toàn bộ test suite (93 unit tests passed)
pytest

# Kiểm tra tĩnh dữ liệu (0 lỗi trên 45 file nguồn)
mypy 2_src/autoform 3_tests/
```

---

## 🛡️ 4. Bảo mật & Quyền riêng tư

- **Local-First**: Toàn bộ dữ liệu hồ sơ cá nhân chỉ lưu trữ cục bộ tại `~/.autoform/profiles/`.
- **An toàn trường nhạy cảm**: Mật khẩu, Số CMND/CCCD, Thẻ tín dụng KHÔNG BAO GIỜ tự động điền hay lưu trữ.
- **Che giấu PII**: Email, SĐT, Token được tự động mã hóa/ẩn trong file log.

---

## 📄 Giấy phép

Phát hành theo giấy phép MIT License.
