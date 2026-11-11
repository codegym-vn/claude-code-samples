# Sổ thu chi câu lạc bộ

Ứng dụng web nhỏ giúp thủ quỹ một câu lạc bộ sinh viên quản lý quỹ: danh sách thành viên, khoản thu (quỹ tháng, ủng hộ), khoản chi, số dư quỹ, báo cáo tháng và danh sách thành viên chưa đóng quỹ.

Đây là ứng dụng mẫu của khóa học "Lập trình với Claude Code". Bạn sẽ fork kho này và làm việc trên nó cùng Claude Code trong suốt khóa học.

## Yêu cầu

- Python 3.11 trở lên
- Git

## Cài đặt và chạy

```bash
# 1. Tạo môi trường ảo và cài thư viện
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Tạo tệp cấu hình riêng của máy bạn
cp .env.example .env               # Windows: copy .env.example .env

# 3. Nạp dữ liệu mẫu (chỉ cần làm một lần)
python -m scripts.seed

# 4. Chạy ứng dụng
uvicorn app.main:app --reload
```

Mở trình duyệt tại http://127.0.0.1:8000 và đăng nhập bằng một trong hai tài khoản thử:

| Tên đăng nhập | Mật khẩu | Vai trò |
|---|---|---|
| `thuquy` | `thuquy123` | Thủ quỹ: ghi thu, ghi chi, hủy khoản chi, xem báo cáo |
| `thanhvien` | `thanhvien123` | Thành viên: chỉ xem |

Muốn nạp lại dữ liệu mẫu từ đầu: `python -m scripts.seed --reset` (lệnh này xóa toàn bộ dữ liệu đang có trong cơ sở dữ liệu cục bộ).

## Chạy kiểm thử

```bash
pytest
```

Chạy một tệp hoặc một kiểm thử:

```bash
pytest tests/test_reports.py
pytest tests/test_reports.py::test_monthly_report_totals
```

## Cấu trúc thư mục

```
app/
  main.py          tạo ứng dụng FastAPI, gắn các nhóm route
  config.py        đọc cấu hình từ .env
  db.py            kết nối SQLite, tạo bảng từ schema.sql
  auth.py          đăng nhập thử và kiểm tra vai trò
  money.py         xử lý số tiền
  dates.py         xử lý ngày tháng
  models.py        lớp dữ liệu Member, Income, Expense
  services/        nghiệp vụ: thành viên, sổ thu chi, báo cáo
  routes/          các trang web
  templates/       giao diện Jinja2
scripts/seed.py    nạp dữ liệu mẫu
tests/             kiểm thử pytest
docs/issues/       phiếu báo lỗi và yêu cầu từ thủ quỹ
docs/ideas.md      ý tưởng chức năng cho dự án cuối khóa
```

## Lưu ý

- Ứng dụng chỉ dùng cho học tập. Tài khoản và mật khẩu ở trên là tài khoản thử, không dùng cho dữ liệu thật.
- Không đưa tệp `.env` và tệp cơ sở dữ liệu lên Git (đã có trong `.gitignore`).
