# Kế hoạch V5 — trang CIA Mission 1000 câu

> Ghi lúc 2026-09-29. TJ tạm dừng ("lát bàn rồi tính tiếp"). Chưa sửa code gì. V4 giữ nguyên, V5 sẽ là file mới.

## Tình hình V4 (đã dò)
- Giao diện (nút, hướng dẫn, tên Phần/bài, checklist, bảng chọn giọng) toàn **tiếng Việt**. Mỗi câu hiện đủ 4 dòng EN/ES/CN/VN.
- **"★ Chỉ hiện câu sống còn"** (`#toggleSurvival`): lọc còn **320/1000 câu** có class `card survival` (viền vàng + ★). Danh sách **cố định**, do Claude chọn lúc soạn. CSS: `.hide-normal .card:not(.survival){display:none}`.
- **★ trên thẻ chỉ là nhãn** (`<span class="star">`), KHÔNG bấm được. TJ tưởng là nút bookmark. Hiện **chưa có bookmark**.

## TJ đã chọn
1. **B2: đổi ngôn ngữ giao diện** — nút 🌐 **VI / EN / ES / 中文** đổi chữ trên nút, hướng dẫn, tên Phần/bài (dòng nghĩa VN giữ nguyên). **KHÔNG** làm B1 (lọc bật/tắt từng dòng ngôn ngữ).
2. **Bookmark 🔖: "tính sau"** — chưa làm. Đề xuất đang chờ: nút 🔖 mỗi thẻ + lọc "Câu đã lưu (N)", lưu localStorage theo máy, đổi nhãn ★ → 🔥 Sống còn, GA4 event `bookmark_add`; bản đồng bộ nhiều máy cần Supabase.

## Cần bàn tiếp trước khi làm B2
- Tên Phần/bài (vd "A1 · Giới thiệu bản thân & công ty") cần dịch sang EN/ES/CN — dịch hết hay chỉ nút + hướng dẫn?
- Mặc định mở trang bằng ngôn ngữ nào (VI, hay theo ngôn ngữ trình duyệt)?
- Sau khi làm: kiểm thử bằng Chrome chạy ngầm, cập nhật `index.html` trỏ sang V5, giữ GA4 `G-8W2S7SP8WN` + các event hiện có, thêm event `change_ui_lang`.

## ✅ Đã làm B2 (2026-09-29) — `Operation_0-Chunks_1000_cau_EN_ES_CN_VN_v5.html`
- TJ chốt: **mở trang mặc định tiếng Anh**. Lần 1 chỉ dịch nút + hướng dẫn; xem thử thấy lệch nên TJ chọn **dịch luôn tên Phần/bài, bối cảnh + mức lịch sự, tiêu đề bài đọc, tiêu đề checklist** (nội dung câu, nghĩa VN, các mục checklist giữ nguyên).
- Tên Phần/bài: phần tử có `data-tk` → bảng `TK` trong JS (vi/en/es/zh). GA4 vẫn gửi tên gốc tiếng Việt (`data-ga`) để số liệu không bị tách theo ngôn ngữ.
- Ô chọn 🌐 VI / EN / ES / 中文 đầu thanh công cụ; nhớ theo máy (localStorage `op0-uilang`). HTML tĩnh đã là tiếng Anh nên không bị nháy chữ Việt khi tải.
- Dịch: thanh công cụ, đoạn hướng dẫn đầu trang + đầu Phần 5, nút/tooltip Phần–nhiệm vụ–câu–bài đọc, ô "Từ vựng chủ chốt", bảng 🎙 giọng đọc, thanh phát nổi, dòng trạng thái, tooltip "chưa có nghĩa".
- GA4 giữ `G-8W2S7SP8WN` + thêm event `change_ui_lang` (`ui_lang`). `index.html` trỏ sang V5.
- Kiểm thử Chrome chạy ngầm: 4 ngôn ngữ đổi đúng, nút bật/tắt giữ trạng thái, bảng giọng đổi ngay khi đang mở, tải lại nhớ ngôn ngữ, không lỗi JS.
- Bookmark 🔖 vẫn "tính sau".
