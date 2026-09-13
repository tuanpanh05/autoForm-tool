<div align="center">

# ⚡ AutoForm — Intelligent Form Auto-Fill Engine

**Hệ thống tự động hóa điền biểu mẫu trực tuyến thông minh, kết hợp Browser Automation & Semantic Mapping.**

[![Python Version](https://img.shields.io/badge/python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Tests Status](https://img.shields.io/badge/tests-93%20passed%20(100%25)-2ea44f?style=for-the-badge&logo=pytest&logoColor=white)](3_tests/)
[![Typing Coverage](https://img.shields.io/badge/mypy-strict%20(0%20errors)-blue?style=for-the-badge&logo=python&logoColor=white)](2_src/autoform/)
[![Architecture](https://img.shields.io/badge/architecture-DDD%20%2F%20Clean-orange?style=for-the-badge)](1_docs/02_architecture/ARCHITECTURE.md)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)

[Tính năng](#-tính-năng-nổi-bật) •
[Kiến trúc](#-kiến-trúc-hệ-thống--cấu-trúc-dự-án) •
[Khởi chạy](#-hướng-dẫn-khởi-chạy-nhanh) •
[Tài liệu](#-chỉ-mục-tài-liệu-kỹ-thuật-1_docs) •
[Bảo mật](#-bảo-mật--quyền-riêng-tư)

</div>

---

## 🌟 Tổng quan dự án

**AutoForm** là ứng dụng tự động điền biểu mẫu trực tuyến thế hệ mới bằng Python, được thiết kế theo nguyên lý **Domain-Driven Design (DDD)** và **Clean Architecture**. Khác với các script tự động hóa đơn giản, AutoForm sử dụng quy trình làm việc 2 giai đoạn **Human-in-the-Loop** giúp loại bỏ rủi ro nộp dữ liệu nhầm lẫn:

```text
               +-------------------------------------------------------------+
               |                  Quy trình hoạt động AutoForm               |
               +-------------------------------------------------------------+
                                              |
     [Form URL] ──>  1. Phân tích Form (Form Inspection & Label Extraction)
                                              |
                ──>  2. Ánh xạ trường (Rule-based & Fuzzy Matcher Engine)
                                              |
                ──>  3. Phê duyệt (Review & Approve: HIGH 🟢 / MED 🟡 / LOW 🔴)
                                              |
                ──>  4. Tự động điền (Autofill Engine & Human-like Delays)
                                              |
                ──>  5. Nộp Form (Confirmation & Submit)
```

---

## ✨ Tính năng nổi bật

- 🤖 **Semantic Field Mapping**: Kết hợp `RuleMatcher` (từ đồng nghĩa Anh/Việt) và `FuzzyMatcher` (Levenshtein Token Ratio) để khớp chính xác nhãn câu hỏi với hồ sơ người dùng.
- 🎯 **Multi-Platform Support**: Hỗ trợ biểu mẫu HTML tiêu chuẩn và nhận diện cấu trúc đặc thù của **Google Forms** (DOM div-based, ARIA roles, data attributes).
- 🛡️ **Safety & Privacy-First**: 
  - Lưu trữ hồ sơ hoàn toàn cục bộ (`Local-First JSON`).
  - Tự động loại trừ trường Mật khẩu, Thẻ tín dụng, Số CMND/CCCD.
  - Tự động mã hóa/che giấu dữ liệu PII (`[REDACTED]`) trong log hệ thống.
  - Tự động phát hiện CAPTCHA trước khi Submit.
- 🎨 **Rich Terminal CLI UI**: Giao diện dòng lệnh Rich sắc nét, hiển thị bảng điểm số tin cậy theo mã màu trực quan (`HIGH` 🟢, `MEDIUM` 🟡, `LOW` 🔴).
- ⚡ **Human-like Automation**: Giả lập hành vi nhập liệu của con người với khoảng trễ ngẫu nhiên (`Random Delays`) giúp tránh bị chặn bởi các cơ chế Anti-bot.

---

## 📁 Kiến trúc hệ thống & Cấu trúc dự án

Dự án được sắp xếp theo cấu trúc thư mục đánh số phân loại chuẩn mực:

```text
autoForm-tool/
├── 1_docs/                     # Tài liệu kiến trúc & đặc tả kỹ thuật Tiếng Việt
│   ├── 01_requirements/        # 📄 Đặc tả Yêu cầu phần mềm (REQUIREMENTS.md)
│   ├── 02_architecture/        # 📄 Kiến trúc hệ thống & Quyết định thiết kế (ARCHITECTURE.md, ADRs)
│   ├── 03_design/              # 📄 Thiết kế kỹ thuật chi tiết các Engine & Schema (TECHNICAL_DESIGN.md)
│   ├── 04_research/            # 📄 Phân tích bài toán & So sánh công nghệ (PROJECT_DISCOVERY.md)
│   ├── 05_security/            # 📄 Chính sách bảo mật & Redact PII (SECURITY.md)
│   ├── 06_testing/             # 📄 Chiến lược & Chuẩn mực kiểm thử (TEST_STRATEGY.md)
│   ├── 07_ROADMAP.md           # 📄 Tiến độ hoàn thành 12 Phase
│   └── INDEX.md                # 📄 Trang chỉ mục tổng hợp Master Index
├── 2_src/autoform/             # Mã nguồn Core Package (100% Strict Type Annotations)
│   ├── cli/                    # Rich Terminal CLI Application & Display Utilities
│   ├── domain/                 # Models, Enums & Domain Exceptions
│   ├── infrastructure/         # Config Manager, Structured Logging & File Storage
│   ├── form_analyzer/          # Form Inspection & Platform Adapters (Generic, Google Forms)
│   ├── mapping/                # Rule & Fuzzy Mapping Engine + Confidence Scorer
│   ├── automation/             # Autofill Engine & Human-like Delay Controller
│   ├── browser/                # Playwright Browser Engine Adapter
│   ├── profile/                # Profile Manager & Storage CRUD
│   ├── validation/             # Field Value Validators (Email, Phone, Date, Regex)
│   └── security/               # PII Redaction Processors & Safety Guards
├── 3_tests/                    # Pytest Suite (93 Unit Tests - 100% Passed)
│   └── unit/                   # Unit tests cho models, mapping, storage, validators, adapters
├── 4_configs/                  # Configuration TOML templates & Environment settings
└── 5_test_forms/               # Mẫu HTML Form thử nghiệm cho E2E Testing
```

---

## 🚀 Hướng dẫn khởi chạy nhanh

### 1. Yêu cầu hệ thống
- Python **3.11+**
- Trình duyệt Chromium (được tự động cài qua Playwright)

### 2. Cài đặt môi trường

```bash
# 1. Clone repository về máy
git clone https://github.com/tuanpanh05/autoForm-tool.git
cd autoForm-tool

# 2. Tạo và kích hoạt môi trường ảo
python -m venv .venv
.venv\Scripts\activate      # Trên Windows (PowerShell)
# source .venv/bin/activate # Trên Linux/macOS

# 3. Cài đặt các thư viện phụ thuộc ở chế độ Editable
pip install -e ".[dev]"

# 4. Cài đặt trình duyệt Playwright
playwright install chromium
```

### 3. Khởi chạy ứng dụng

```bash
# Khởi chạy giao diện tương tác Rich Terminal (Menu phân tích -> Phê duyệt -> Điền -> Nộp)
python -m autoform

# Chạy lệnh điền nhanh trực tiếp qua CLI
autoform fill-form "https://docs.google.com/forms/d/e/..." --profile default

# Xem thông tin và quản lý Profile người dùng
autoform profiles list
autoform profiles show default
```

---

## 📖 Chỉ mục tài liệu kỹ thuật (`1_docs/`)

Toàn bộ tài liệu hướng dẫn và thiết kế hệ thống bằng Tiếng Việt tại [1_docs/INDEX.md](1_docs/INDEX.md):

1. 📖 **[Cẩm nang Hướng dẫn Sử dụng (USER_GUIDE.md)](1_docs/USER_GUIDE.md)** — Hướng dẫn cài đặt, tạo Profile & vận hành tự động điền Form chi tiết từ A-Z.
2. 📄 **[Yêu cầu hệ thống (REQUIREMENTS.md)](1_docs/01_requirements/REQUIREMENTS.md)** — Đặc tả chi tiết các yêu cầu chức năng & phi chức năng.
3. 📄 **[Kiến trúc hệ thống (ARCHITECTURE.md)](1_docs/02_architecture/ARCHITECTURE.md)** — Mô hình phân tầng Clean Architecture & Sơ đồ luồng dữ liệu.
4. 📄 **[Nhật ký quyết định (ADR Log)](1_docs/02_architecture/ARCHITECTURE_DECISIONS.md)** — Lý do lựa chọn Playwright, Local-First & Pluggable Adapters.
5. 📄 **[Thiết kế kỹ thuật (TECHNICAL_DESIGN.md)](1_docs/03_design/TECHNICAL_DESIGN.md)** — Thuật toán trích xuất nhãn 9 tầng & Động cơ ánh xạ.
6. 📄 **[Thiết kế Schema Form (FORM_SCHEMA.md)](1_docs/03_design/FORM_SCHEMA.md)** — Cấu trúc dữ liệu biểu diễn Form & các Enums.
7. 📄 **[Engine Tự động điền (AUTOMATION_ENGINE.md)](1_docs/03_design/AUTOMATION_ENGINE.md)** — Chiến lược điền theo loại trường & Phân phối trễ ngẫu nhiên.
8. 📄 **[Báo cáo Bảo mật (SECURITY.md)](1_docs/05_security/SECURITY.md)** — Nguyên tắc che giấu dữ liệu PII & An toàn dữ liệu nhạy cảm.
9. 📄 **[Chiến lược Kiểm thử (TEST_STRATEGY.md)](1_docs/06_testing/TEST_STRATEGY.md)** — Cấu trúc test suite & Chuẩn mực bao phủ code.
10. 📄 **[Lộ trình phát triển (ROADMAP.md)](1_docs/07_ROADMAP.md)** — Tiến độ hoàn thành toàn bộ 12 Phase của dự án.

---

## 🧪 Kiểm thử & Chất lượng mã nguồn

Dự án tuân thủ tiêu chuẩn chất lượng cao với 100% Type Annotation và Test Suite tự động:

```bash
# Chạy toàn bộ Test Suite (93 unit tests passed)
pytest

# Kiểm tra tĩnh dữ liệu với Mypy Strict Mode (0 lỗi trên 45 file nguồn)
mypy 2_src/autoform 3_tests/
```

**Kết quả kiểm thử thực tế:**
```text
============================= 93 passed in 0.25s ==============================
Success: no issues found in 45 source files
```

---

## 🛡️ Bảo mật & Quyền riêng tư

- 🔒 **Local-Only**: Hồ sơ cá nhân của bạn lưu tại `~/.autoform/profiles/` và **KHÔNG BAO GIỜ** tải lên đám mây.
- 🚫 **Zero Sensitivity Leak**: Mật khẩu, Thẻ tín dụng, Số tài khoản ngân hàng tuyệt đối không bị ghi nhận hay điền tự động.
- 🙈 **PII Protection**: Mọi dữ liệu email, số điện thoại trong log đều được mã hóa bằng tag `[REDACTED]`.

---

## 📄 License

Dự án được phát hành theo giấy phép **[MIT License](LICENSE)**.

<div align="center">
  <sub>Built with ❤️ by AutoForm Team</sub>
</div>
