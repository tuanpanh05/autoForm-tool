# Đặc tả Động cơ Ánh xạ Trường dữ liệu (Mapping Engine Specification)

> **Mã tài liệu**: DES-MAP-001  
> **Trạng thái**: Đã duyệt (Approved)  

Tài liệu này quy định chi tiết về kiến trúc, thuật toán và cơ chế tính điểm của Động cơ Ánh xạ (Mapping Engine) trong AutoForm.

---

## 1. Tổng quan Kiến trúc Ánh xạ

`MappingEngine` chịu trách nhiệm so sánh nhãn của từng trường trên Form với danh sách tất cả các trường dữ liệu hiện có trong `UserProfile` để tìm ra đường dẫn Profile tương thích nhất.

```text
FormField (Label, Type, Context)  +  UserProfile (Personal, Contact, Work, Education, Custom)
                                   |
                                   v
                       +-----------------------+
                       |     RuleMatcher       | ---> Exact/Alias Matches (Score: 0.90 - 1.00)
                       +-----------------------+
                                   |
                                   v
                       +-----------------------+
                       |    FuzzyMatcher       | ---> Token Set Ratio Matches (Score: 0.60 - 0.89)
                       +-----------------------+
                                   |
                                   v
                       +-----------------------+
                       |   ConfidenceScorer    | ---> Bonus/Penalty Adjustment & Classification
                       +-----------------------+
                                   |
                                   v
                             FieldMapping
```

---

## 2. Rule-Based Matcher (`RuleMatcher`)

`RuleMatcher` duyệt qua từ điển từ đồng nghĩa được xây dựng sẵn (Alias Dictionary) hỗ trợ song ngữ Tiếng Anh và Tiếng Việt.

### Danh sách Alias mẫu:

| Profile Path | Từ khóa & Từ đồng nghĩa (Anh / Việt) |
|---|---|
| `personal.full_name` | `full name`, `full_name`, `name`, `họ và tên`, `họ tên`, `họ và tên đầy đủ` |
| `contact.email` | `email`, `email address`, `địa chỉ email`, `e-mail` |
| `contact.phone` | `phone`, `phone number`, `telephone`, `mobile`, `số điện thoại`, `sđt` |
| `personal.date_of_birth` | `date of birth`, `dob`, `birthdate`, `ngày sinh`, `ngày tháng năm sinh` |
| `education.university` | `university`, `college`, `school`, `trường đại học`, `trường học` |
| `personal.gender` | `gender`, `sex`, `giới tính` |

---

## 3. Fuzzy String Matcher (`FuzzyMatcher`)

Khi `RuleMatcher` không tìm thấy kết quả khớp tuyệt đối, `FuzzyMatcher` được kích hoạt.
- Sử dụng thuật toán `token_set_ratio` của thư viện `RapidFuzz` để so sánh chuỗi nhãn với tên kỹ thuật của các trường profile.
- Tự động chuẩn hóa văn bản: Chuyển về chữ thường, bỏ dấu tiếng Việt, loại bỏ các từ dư thừa ("Please enter your...", "Nhập...").
- Ngưỡng điểm tối thiểu (Minimum Score Threshold): Mặc định `60`.

---

## 4. Phân cấp Cấp độ Tin cậy (ConfidenceLevel)

| Cấp độ Tin cậy | Ký hiệu & Mã màu | Ngưỡng điểm | Hành vi giao diện CLI |
|---|---|---|---|
| **HIGH** | 🟢 (Xanh lá) | `>= 0.85` | Tự động phê duyệt khi chọn Accept All (`a`) |
| **MEDIUM** | 🟡 (Vàng) | `0.60 – 0.84` | Hiển thị cảnh báo để người dùng kiểm tra kỹ |
| **LOW** | 🔴 (Đỏ) | `0.30 – 0.59` | Khuyến nghị người dùng chỉnh sửa hoặc từ chối |
| **NO_MATCH** | ⚪ (Xám) | `< 0.30` | Bỏ qua, không đề xuất giá trị điền |
