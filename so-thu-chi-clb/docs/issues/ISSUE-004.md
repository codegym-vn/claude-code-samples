# ISSUE-004: Danh sách chưa đóng quỹ có cả người đã rời câu lạc bộ

- Người báo: Trần Thu Hà (thủ quỹ)
- Mức độ: Trung bình, mình suýt nhắn đòi tiền bạn đã rời câu lạc bộ
- Trang liên quan: Chưa đóng quỹ

## Mô tả

Tháng trước hai bạn Đặng Quốc Bảo và Dương Văn Tú đã rời câu lạc bộ, mình đã bấm "Xác nhận rời" trong trang của từng bạn. Nhưng trang "Chưa đóng quỹ" của tháng này vẫn liệt kê hai bạn. Số "người chưa đóng quỹ" ở trang Tổng quan cũng bị tính dư.

## Các bước tái hiện

1. Chạy `python -m scripts.seed --reset` để có dữ liệu mẫu.
2. Đăng nhập bằng tài khoản thủ quỹ.
3. Mở trang "Thành viên": Đặng Quốc Bảo và Dương Văn Tú có trạng thái "Đã rời".
4. Mở trang "Chưa đóng quỹ" của tháng hiện tại.

## Kết quả mong đợi

Danh sách chỉ gồm những thành viên còn sinh hoạt mà chưa đóng quỹ tháng đó.

## Kết quả thực tế

Danh sách có cả Đặng Quốc Bảo và Dương Văn Tú.
