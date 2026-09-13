# Trang chỉ mục tài liệu dự án AutoForm

Chỉ mục tổng hợp toàn bộ các tài liệu hướng dẫn sử dụng, thiết kế kỹ thuật, quyết định kiến trúc (ADR), tài liệu nghiên cứu và đặc tả bài toán của hệ thống AutoForm.

---

## 📁 Danh mục tài liệu

### 0. Hướng dẫn sử dụng & Vận hành (`USER_GUIDE.md`)
- 📖 **[USER_GUIDE.md](USER_GUIDE.md)** — Cẩm nang hướng dẫn cài đặt, quản lý Profile và vận hành tự động điền Form từ A-Z.

### 1. Yêu cầu & Đặc tả bài toán (`01_requirements/`)
- 📄 [REQUIREMENTS.md](01_requirements/REQUIREMENTS.md) — Đặc tả yêu cầu chức năng và phi chức năng của hệ thống.

### 2. Kiến trúc hệ thống (`02_architecture/`)
- 📄 [ARCHITECTURE.md](02_architecture/ARCHITECTURE.md) — Kiến trúc tổng thể hệ thống, sơ đồ thành phần và luồng dữ liệu.
- 📄 [ARCHITECTURE_DECISIONS.md](02_architecture/ARCHITECTURE_DECISIONS.md) — Tổng hợp các quyết định kiến trúc (ADRs).

### 3. Thiết kế chi tiết (`03_design/`)
- 📄 [TECHNICAL_DESIGN.md](03_design/TECHNICAL_DESIGN.md) — Đặc tả thiết kế kỹ thuật chi tiết toàn bộ hệ thống.
- 📄 [FORM_SCHEMA.md](03_design/FORM_SCHEMA.md) — Mô hình biểu diễn Schema Form và phân loại trường.
- 📄 [MAPPING_ENGINE.md](03_design/MAPPING_ENGINE.md) — Động cơ khớp trường thông minh (Rule-based & Fuzzy Matcher).
- 📄 [AUTOMATION_ENGINE.md](03_design/AUTOMATION_ENGINE.md) — Bộ tự động điền form, thực thi hành vi và giả lập độ trễ con người.
- 📄 [AI_DESIGN.md](03_design/AI_DESIGN.md) — Kiến trúc tích hợp LLM & Semantic Embedding (Tính năng v2+).

### 4. Phân tích & Nghiên cứu (`04_research/`)
- 📄 [PROJECT_DISCOVERY.md](04_research/PROJECT_DISCOVERY.md) — Nghiên cứu bài toán, Chân dung người dùng và Phân tích độ phức tạp của Form.
- 📄 [TECHNOLOGY_COMPARISON.md](04_research/TECHNOLOGY_COMPARISON.md) — So sánh và đánh giá công nghệ (Playwright vs Selenium vs Puppeteer).

### 5. Bảo mật & Quyền riêng tư (`05_security/`)
- 📄 [SECURITY.md](05_security/SECURITY.md) — Mô hình bảo mật Local-first, cơ chế Redact dữ liệu PII và bảo vệ trường nhạy cảm.

### 6. Chiến lược kiểm thử (`06_testing/`)
- 📄 [TEST_STRATEGY.md](06_testing/TEST_STRATEGY.md) — Chiến lược kiểm thử, kịch bản test và tiêu chuẩn độ bao phủ mã nguồn.

### 7. Lộ trình phát triển (`07_ROADMAP.md`)
- 📄 [07_ROADMAP.md](07_ROADMAP.md) — Lộ trình chi tiết và cột mốc hoàn thành toàn bộ 12 Phase của dự án.
