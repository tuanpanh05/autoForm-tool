# Nhật ký Quyết định Kiến trúc (Architectural Decision Records - ADRs)

> **Mã tài liệu**: ADR-LOG  
> **Trạng thái**: Đã duyệt (Approved)  

Tài liệu này tổng hợp các quyết định kiến trúc kỹ thuật quan trọng trong quá trình thiết kế và phát triển công cụ AutoForm.

---

## ADR-001: Lựa chọn Playwright làm Engine Browser Automation

- **Bối cảnh**: Cần một thư viện điều khiển trình duyệt hiện đại, tin cậy, hỗ trợ Async/Await native trong Python để tương tác với các ứng dụng Web Forms phức tạp.
- **Quyết định**: Chọn **Playwright Python** thay vì Selenium hay Puppeteer.
- **Lý do**:
  1. Hỗ trợ cơ chế Auto-waiting thông minh cho các phần tử DOM động.
  2. Tốc độ thực thi nhanh hơn Selenium và tiêu tốn ít tài nguyên hơn.
  3. Cung cấp API đánh giá JavaScript (`page.evaluate`) mạnh mẽ và ổn định.
  4. Hỗ trợ chụp ảnh màn hình và quản lý ngữ cảnh trình duyệt (Browser Context) cô lập.

---

## ADR-002: Áp dụng Mô hình Điền Form 2 Giai đoạn (Human-in-the-Loop Workflow)

- **Bối cảnh**: Các công cụ tự động hóa điền form thông thường dễ bị sai sót khi tự động điền các trường không chính xác, gây rủi ro nộp dữ liệu sai.
- **Quyết định**: Chia luồng tự động hóa thành 2 giai đoạn tách biệt: **Giai đoạn 1 (Phân tích & Ánh xạ)** và **Giai đoạn 2 (Phê duyệt & Điền)**.
- **Lý do**:
  1. Cho phép người dùng kiểm tra bảng điểm số tin cậy (`HIGH`, `MEDIUM`, `LOW`) trước khi nhập liệu.
  2. Đảm bảo nguyên tắc người dùng luôn nắm quyền kiểm soát cuối cùng đối với dữ liệu cá nhân của mình.
  3. Tránh việc tự động nộp Form (`Auto-submit`) ngoài ý muốn.

---

## ADR-003: Phân tầng Matchers thành Rule-based & Fuzzy Matcher

- **Bối cảnh**: Nhãn của các trường trên Form trực tuyến rất đa dạng (tiếng Anh, tiếng Việt, viết tắt, câu hỏi dài). Một thuật toán duy nhất không thể vừa chính xác tuyệt đối vừa linh hoạt.
- **Quyết định**: Kết hợp nhiều Matcher theo tầng: **RuleMatcher** (khớp từ khóa/từ đồng nghĩa chuẩn) chạy trước, sau đó đến **FuzzyMatcher** (khớp chuỗi mờ Levenshtein).
- **Lý do**:
  1. `RuleMatcher` đảm bảo tốc độ cực nhanh và độ chính xác 100% đối với các từ khóa phổ biến ("Email", "Họ và tên", "Số điện thoại").
  2. `FuzzyMatcher` xử lý tốt các câu hỏi dạng diễn giải dài hoặc lỗi chính tả nhỏ.
  3. Dễ dàng bổ sung thêm các Matcher thông minh khác (Semantic Embedding, LLM) trong tương lai.

---

## ADR-004: Kiến trúc Pluggable Form Adapters

- **Bối cảnh**: Các nền tảng Form trực tuyến (HTML chuẩn, Google Forms, Microsoft Forms, Typeform) có cấu trúc DOM hoàn toàn khác nhau.
- **Quyết định**: Định nghĩa giao diện chung `FormAdapter` và áp dụng **Factory Pattern** để tải Adapter phù hợp theo URL.
- **Lý do**:
  1. Tách biệt logic phân tích từng nền tảng khỏi luồng xử lý chính của Orchestrator.
  2. Cho phép đóng góp và mở rộng thêm các Adapter nền tảng mới mà không ảnh hưởng đến các Module hiện có.

---

## ADR-005: Chính sách lưu trữ dữ liệu Cục bộ (Local-First Storage)

- **Bối cảnh**: Dữ liệu hồ sơ cá nhân (Họ tên, Email, SĐT, Học vấn) là dữ liệu nhạy cảm riêng tư.
- **Quyết định**: Lưu trữ toàn bộ Profile dưới dạng các file JSON định dạng rõ ràng trong thư mục cục bộ của người dùng (`~/.autoform/profiles/`).
- **Lý do**:
  1. Đảm bảo 100% quyền riêng tư (Privacy-first), không phụ thuộc vào kết nối Internet hay Server trung gian.
  2. Người dùng dễ dàng sao lưu, chỉnh sửa hoặc xóa bỏ dữ liệu bất kỳ lúc nào.
