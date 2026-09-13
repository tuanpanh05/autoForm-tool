# Báo cáo So sánh & Đánh giá Công nghệ (Technology Comparison)

> **Mã tài liệu**: RES-TECH-001  
> **Trạng thái**: Đã duyệt (Approved)  

Tài liệu này chi tiết hóa quá trình đánh giá và lý do lựa chọn các công nghệ cốt lõi phục vụ phát triển ứng dụng AutoForm.

---

## 1. So sánh các Framework Trình điều khiển Trình duyệt (Browser Automation)

| Tiêu chí | Playwright Python (Được chọn) | Selenium WebDriver | Puppeteer (Pyppeteer) |
|---|---|---|---|
| **Cơ chế chờ (Auto-waiting)** | 🟢 Tự động chờ phần tử hiển thị/khả dụng | 🔴 Phải tự viết `WebDriverWait` thủ công | 🟡 Khá tốt nhưng phụ thuộc Chrome |
| **Tốc độ thực thi** | 🟢 Cực nhanh (Websocket CDP protocol) | 🔴 Chậm (HTTP Webdriver overhead) | 🟢 Nhanh |
| **Async/Await Support** | 🟢 Hỗ trợ Asyncio Native 100% | 🔴 Hỗ trợ kém / Blocking I/O | 🟢 Hỗ trợ Async |
| **Đánh giá JS (`evaluate`)** | 🟢 Trả về giá trị JSON/Primitive mượt mà | 🟡 Phức tạp hơn | 🟢 Tốt |
| **Độ ổn định Selector** | 🟢 Hỗ trợ CSS, XPath, Text, ARIA role | 🟡 Chủ yếu CSS & XPath | 🟡 CSS & XPath |

👉 **Kết luận**: **Playwright Python** là sự lựa chọn tối ưu nhất về tốc độ, tính hiện đại và khả năng hỗ trợ Async native trong Python.

---

## 2. So sánh các Thư viện Ghép nối chuỗi (String Matching Libraries)

| Tiêu chí | RapidFuzz (Được chọn) | FuzzyWuzzy / difflib | Spacy / Sentence-Transformers |
|---|---|---|---|
| **Tốc độ xử lý** | 🟢 Cực nhanh (C++ implementation) | 🔴 Chậm khi chạy số lượng lớn | 🔴 Nặng, tốn CPU/RAM |
| **Độ chính xác chuỗi ngắn** | 🟢 Rất cao với `token_set_ratio` | 🟡 Khá | 🟢 Rất cao về mặt ngữ nghĩa |
| **Yêu cầu Tài nguyên** | 🟢 Cực nhẹ, không cần GPU/Model | 🟢 Nhẹ | 🔴 Yêu cầu tải weights vài trăm MB |

👉 **Kết luận**: **RapidFuzz** được chọn cho bản MVP do tốc độ tính toán dưới `1ms`, không tốn tài nguyên phần cứng. Các mô hình Sentence-Transformers sẽ được tích hợp dưới dạng tùy chọn ở phiên bản v2+.
