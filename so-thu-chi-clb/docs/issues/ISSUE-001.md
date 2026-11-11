# ISSUE-001: Số dư quỹ không khớp với sổ, hủy khoản chi rồi mà tiền vẫn bị trừ

- Người báo: Trần Thu Hà (thủ quỹ)
- Mức độ: Cao, số dư là con số ban chủ nhiệm hỏi đầu tiên mỗi buổi họp
- Trang liên quan: Tổng quan

## Mô tả

Số dư quỹ trên trang Tổng quan thấp hơn nhiều so với số mình tự cộng tay. Mình cộng tổng cột "Khoản thu" rồi trừ tổng chi ở cuối trang "Khoản chi" thì ra một số dương, nhưng trang Tổng quan lại báo số âm. Tháng trước mình có hủy khoản đặt cọc thuê xe 1.500.000 đ vì chuyến dã ngoại bị hoãn, mình nghi là có liên quan nhưng không chắc.

## Các bước tái hiện

1. Đăng nhập bằng tài khoản thủ quỹ, mở trang Tổng quan, ghi lại số dư quỹ (gọi là X).
2. Vào "Khoản chi", ghi một khoản chi mới 100.000 đ.
3. Quay lại Tổng quan: số dư là X trừ 100.000 đ. Chỗ này đúng.
4. Vào "Khoản chi", bấm "Hủy" khoản vừa ghi, lý do "Nhập nhầm". Khoản chi hiện trạng thái "Đã hủy".
5. Quay lại Tổng quan.

## Kết quả mong đợi

Số dư quay về X, vì khoản chi đã hủy không còn là tiền đã tiêu.

## Kết quả thực tế

Số dư vẫn là X trừ 100.000 đ. Trang "Khoản chi" thì ghi tổng chi đúng (không tính khoản đã hủy), nên hai trang lệch nhau.
