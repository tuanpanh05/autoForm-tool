# Tài liệu Kiến trúc Hệ thống AutoForm (System Architecture)

> **Mã tài liệu**: ARCH-001  
> **Trạng thái**: Đã duyệt (Approved)  
> **Phiên bản**: 1.0.0  

---

## 1. Tổng quan Kiến trúc

AutoForm được thiết kế theo nguyên lý **Domain-Driven Design (DDD)** kết hợp với **Clean / Hexagonal Architecture**. Hệ thống chia tách rõ ràng giữa Core Logic (Domain & Application) với các thành phần phụ thuộc bên ngoài (Browser Adapter, File Storage, CLI UI).

---

## 2. Sơ đồ Kiến trúc Phân tầng (Layered Architecture Diagram)

```text
+-----------------------------------------------------------------------+
|                         Giao diện CLI (Rich UI)                        |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    Application Layer (Orchestrator)                   |
+-----------------------------------------------------------------------+
     |                              |                             |
     v                              v                             v
+------------------+     +--------------------+        +----------------+
|  Form Analyzer   |     |   Mapping Engine   |        |    Autofill    |
|     Adapters     |     |  (Rule & Fuzzy)    |        |     Engine     |
+------------------+     +--------------------+        +----------------+
     |                              |                             |
     +------------------------------+-----------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                         Domain Layer (Models/Enums)                   |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                  Infrastructure Layer (Config/Log/Store)              |
+-----------------------------------------------------------------------+
```

---

## 3. Các Phân hệ chính (Core Subsystems)

### 3.1 Domain Layer (`autoform.domain`)
- Chứa các đối tượng nghiệp vụ cốt lõi: `FormField`, `FormSchema`, `UserProfile`, `FieldMapping`, `FillResult`, `SubmitResult`.
- Đảm bảo tính toàn vẹn dữ liệu thông qua các Enum: `FieldType`, `ConfidenceLevel`, `MatchMethod`, `LabelSource`, `Platform`.
- Tuyệt đối KHÔNG phụ thuộc vào bất kỳ thư viện bên ngoài nào.

### 3.2 Form Analyzer Engine (`autoform.form_analyzer`)
- Áp dụng **Factory Pattern** (`FormAdapterFactory`) để tự động nhận diện nền tảng Form dựa trên URL.
- **GenericHTMLFormAdapter**: Phân tích biểu mẫu HTML chuẩn dựa trên thuật toán 9 tầng trích xuất label.
- **GoogleFormsAdapter**: Phân tích biểu mẫu Google Forms dựa trên cấu trúc DOM div-based và các thuộc tính ARIA role (`data-params`, `role="radio"`, `role="checkbox"`).

### 3.3 Mapping & Intelligence Engine (`autoform.mapping`)
- **RuleMatcher**: Khớp từ khóa chính xác/chứa từ dựa trên từ điển từ đồng nghĩa (hỗ trợ cả tiếng Anh lẫn tiếng Việt).
- **FuzzyMatcher**: Khớp chuỗi mờ sử dụng thuật toán Levenshtein / RapidFuzz ratio với ngưỡng có thể cấu hình.
- **ConfidenceScorer**: Tính toán điểm số tổng hợp (0.0 – 1.0) kết hợp với điểm thưởng/phạt theo kiểu trường dữ liệu và ngữ cảnh section.

### 3.4 Autofill Engine (`autoform.automation`)
- Nhận danh sách các ánh xạ đã được phê duyệt (`FieldMapping` với `approved = True`).
- Thực thi hành động nhập liệu trên trình duyệt thông qua `BrowserAdapter`.
- Giả lập hành vi con người bằng ngẫu nhiên hóa độ trễ (Random Delays) giữa các trường và các lần nhấp chuột.
- Kiểm tra an toàn loại bỏ trường nhạy cảm và phát hiện CAPTCHA trước khi submit.

### 3.5 Infrastructure & Browser (`autoform.infrastructure` & `autoform.browser`)
- **PlaywrightAdapter**: Triển khai `BrowserAdapter` đóng gói toàn bộ tương tác trình duyệt thông qua thư viện Playwright.
- **ProfileStorage**: Quản lý lưu trữ/đọc file JSON profile cục bộ.
- **Config & Logging**: Quản lý cấu hình TOML, biến môi trường và ghi log JSON chuẩn cấu trúc với cơ chế Redact dữ liệu PII.

---

## 4. Luồng dữ liệu hệ thống (Data Flow Sequence)

```text
User CLI           Orchestrator          FormAnalyzer         MappingEngine         AutofillEngine         Browser
   |                    |                     |                    |                      |                   |
   |--- 1. analyze ---->|                     |                    |                      |                   |
   |                    |--- 2. open & detect>|                    |                      |                   |
   |                    |                     |--- 3. extract ---->|                      |                   |
   |                    |<-- 4. FormSchema ---|                    |                      |                   |
   |                    |                     |                    |                      |                   |
   |                    |--- 5. map_form ------------------------->|                      |                   |
   |                    |<-- 6. FieldMappings ---------------------|                      |                   |
   |<-- 7. Display Table|                     |                    |                      |                   |
   |                    |                     |                    |                      |                   |
   |--- 8. Approve ---->|                     |                    |                      |                   |
   |                    |--- 9. fill_form ----------------------------------------------->|                   |
   |                    |                     |                    |                      |--- 10. interact ->|
   |                    |<-- 11. FillResult ----------------------------------------------|<-- 12. Success ---|
   |<-- 13. Summary ----|                     |                    |                      |                   |
```

---

## 5. Các nguyên tắc thiết kế kỹ thuật (Design Principles)

1. **Single Responsibility Principle (SRP)**: Mỗi module chỉ đảm nhiệm một công việc duy nhất (Analyzer chỉ trích xuất, Matcher chỉ tính điểm, Autofill chỉ nhập liệu).
2. **Open/Closed Principle (OCP)**: Dễ dàng mở rộng thêm các Adapter nền tảng mới (Microsoft Forms, Typeform) mà không cần sửa đổi Core Pipeline.
3. **Dependency Inversion Principle (DIP)**: Core logic phụ thuộc vào các Interface trừu tượng (`BrowserAdapter`, `FormAdapter`, `Matcher`) thay vì triển khai cụ thể.
4. **Safety-First Automation**: Ưu tiên sự an toàn dữ liệu và quyền kiểm soát của người dùng hơn việc tự động hóa mù quáng.
