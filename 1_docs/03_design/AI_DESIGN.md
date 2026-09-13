# Kiến trúc Tích hợp AI & Semantic Embedding (AI Architecture - Phase v2+)

> **Mã tài liệu**: DES-AI-001  
> **Trạng thái**: Dự thảo (Draft - Đã lập kế hoạch cho v2+)  

Tài liệu này quy định kiến trúc tích hợp các mô hình trí tuệ nhân tạo (LLM & Vector Embeddings) để nâng cao khả năng ánh xạ các form có câu hỏi phức tạp hoặc đa ngôn ngữ.

---

## 1. Tổng quan Kiến trúc AI

```text
[Form Field Label / Description]  +  [Profile Fields Data]
                                       |
                                       v
                        +-----------------------------+
                        | Semantic Embedding Matcher  | ---> Cosine Similarity (Sentence Transformers)
                        +-----------------------------+
                                       | (Fallback nếu điểm < Threshold)
                                       v
                        +-----------------------------+
                        |     LLM Mapping Matcher     | ---> OpenAI GPT-4o-mini / Local LLM Prompt
                        +-----------------------------+
```

---

## 2. Các nguyên tắc bảo mật thông tin khi dùng AI (AI Privacy Safeguards)

1. **Không bao giờ gửi giá trị dữ liệu (No Values Sent)**: Chỉ gửi Nhãn trường (`label`), Mô tả (`description`) và Đường dẫn Profile (`profile_path`). Tuyệt đối KHÔNG bao giờ gửi giá trị dữ liệu cá nhân (như họ tên thật, email thật, số điện thoại) lên các API AI bên ngoài.
2. **Local Embedding Preferred**: Ưu tiên sử dụng mô hình Sentence Transformer chạy cục bộ (`all-MiniLM-L6-v2`) để tính toán vectơ ngữ nghĩa hoàn toàn Offline.
3. **Opt-in Feature**: Tính năng AI mặc định bị TẮT (`enable_ai = false` trong cấu hình), người dùng chỉ kích hoạt khi chủ động cài đặt API Key.
