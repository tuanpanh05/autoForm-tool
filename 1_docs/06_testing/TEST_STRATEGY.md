# Chiến lược Kiểm thử & Đảm bảo Chất lượng (Test Strategy Specification)

> **Mã tài liệu**: TST-001  
> **Trạng thái**: Đã duyệt (Approved)  

Tài liệu này quy định chiến lược kiểm thử tự động, cấu trúc test suite và tiêu chuẩn độ bao phủ mã nguồn cho dự án AutoForm.

---

## 1. Cấu trúc Test Suite

Hệ thống test suite được xây dựng dựa trên framework **Pytest** và đặt tại thư mục `3_tests/`:

```text
3_tests/
└── unit/
    ├── test_models.py           # Test Domain Models, FieldType, UserProfile path get/set
    ├── test_mapping.py          # Test RuleMatcher, FuzzyMatcher, ConfidenceScorer, MappingEngine
    ├── test_validators.py       # Test Email, Phone, Date, Number, URL, Length Validators
    ├── test_generic_adapter.py  # Test GenericHTMLFormAdapter & _humanize helper
    └── test_google_forms.py     # Test GoogleFormsAdapter can_handle & title/captcha extraction
```

---

## 2. Tiêu chuẩn Kiểm thử & Độ bao phủ (Coverage Standards)

- **Tổng số Unit Tests hiện tại**: `93 passed` (100% pass rate).
- **Thời gian thực thi Test Suite**: `< 0.5s` (đảm bảo tốc độ chạy cực nhanh trên CI/CD).
- **Yêu cầu Độ bao phủ (Code Coverage)**: Tối thiểu **80%** trên toàn bộ các file nguồn `2_src/autoform`.

---

## 3. Các nhóm Test Case tiêu biểu (Key Test Scenarios)

1. **Domain Models & Enums**:
   - Truy vấn trường dữ liệu hợp lệ/không hợp lệ theo đường dẫn phân cấp (`personal.full_name`, `contact.email`).
   - Kiểm tra mã hóa và giải mã JSON roundtrip cho `UserProfile` và `FormField`.

2. **Matching Algorithms & Confidence**:
   - Khớp từ khóa tiếng Anh/tiếng Việt bằng `RuleMatcher`.
   - Khớp chuỗi mờ bằng `FuzzyMatcher` và giới hạn kết quả Top 5.
   - Kiểm tra tính toán điểm thưởng/phạt loại trường của `ConfidenceScorer`.

3. **Validation Suite**:
   - Kiểm tra định dạng Email hợp lệ / không hợp lệ.
   - Kiểm tra số điện thoại chuẩn quốc tế và Việt Nam.
   - Kiểm tra các định dạng ngày tháng ISO `YYYY-MM-DD` và `DD/MM/YYYY`.

4. **Adapters & HTML Parsing**:
   - Kiểm tra hàm làm sạch nhãn `_humanize("txtEmailAddress")` → `"Email Address"`.
   - Kiểm tra phát hiện URL Google Forms (`can_handle`).
