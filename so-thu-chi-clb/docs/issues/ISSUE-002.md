# ISSUE-002: Báo cáo tháng thiếu tiền so với danh sách khoản thu

- Người báo: Trần Thu Hà (thủ quỹ)
- Mức độ: Cao, báo cáo tháng phải nộp cho ban chủ nhiệm
- Trang liên quan: Báo cáo tháng, Khoản thu

## Mô tả

Tổng thu trên trang "Báo cáo tháng" của tháng trước thấp hơn tổng ở trang "Khoản thu" khi mình lọc đúng tháng đó. Ví dụ hôm mình kiểm báo cáo tháng 10/2026: trang Khoản thu lọc tháng 10 cho tổng 800.000 đ, còn báo cáo tháng 10 chỉ có 350.000 đ. Tổng chi trong báo cáo cũng có vẻ thấp hơn thực tế. Mình so từng dòng thì thấy thiếu một số khoản, nhưng không phải khoản nào cũng thiếu, và tháng nào cũng bị.

Trang Khoản thu thì mình đã đối chiếu với sổ tay, trang đó đúng.

## Các bước tái hiện

1. Chạy `python -m scripts.seed --reset` để có dữ liệu mẫu.
2. Đăng nhập bằng tài khoản thủ quỹ.
3. Mở "Khoản thu", lọc theo tháng trước, ghi lại số ở dòng "Tổng cộng".
4. Mở "Báo cáo tháng", bấm "Tháng trước" để xem đúng tháng đó, đọc ô "Tổng thu".

## Kết quả mong đợi

"Tổng thu" trong báo cáo bằng "Tổng cộng" ở trang Khoản thu của cùng tháng. Tổng chi trong báo cáo bằng tổng các khoản chi còn hiệu lực trong tháng đó.

## Kết quả thực tế

Báo cáo thấp hơn. Trong phần "Chi tiết khoản thu" của báo cáo không thấy một số khoản có trong trang Khoản thu.
