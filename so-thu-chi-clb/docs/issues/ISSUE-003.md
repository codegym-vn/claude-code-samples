# ISSUE-003: Tìm thành viên theo tên không ra người cần tìm

- Người báo: Lê Minh Khang (thành viên, phụ trách điểm danh)
- Mức độ: Trung bình
- Trang liên quan: Thành viên

## Mô tả

Mình tìm bạn Nguyễn Văn An để xem bạn ấy đã đóng quỹ tháng nào. Gõ "an" vào ô tìm kiếm thì ra ba người khác (Thanh Hương, Thu Trang, Thị Lan) nhưng không có bạn An. Gõ "nguyễn" cũng không ra ai, dù câu lạc bộ có bạn họ Nguyễn. Trên điện thoại bàn phím thường gõ chữ thường nên lần nào mình cũng bị.

## Các bước tái hiện

1. Chạy `python -m scripts.seed --reset` để có dữ liệu mẫu.
2. Đăng nhập (tài khoản nào cũng được), vào trang "Thành viên".
3. Gõ "an" vào ô tìm kiếm, bấm "Tìm".
4. Thử thêm với "nguyễn" và "sv2023001".

## Kết quả mong đợi

- "an" tìm thấy Nguyễn Văn An, An Khánh Linh, Ngô Phương Anh và những người có "an" trong tên.
- "nguyễn" tìm thấy Nguyễn Văn An.
- "sv2023001" tìm thấy người có mã SV2023001.

## Kết quả thực tế

- "an" không có Nguyễn Văn An, An Khánh Linh, Ngô Phương Anh.
- "nguyễn" và "sv2023001" báo "Không tìm thấy thành viên nào".
