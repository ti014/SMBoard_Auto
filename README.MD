# SMBoard Automation Tool

Công cụ tự động hóa quy trình khai báo công việc trên SMBoard.

![Demo](/images/1.jpg)
## Features

- 🔄 Tự động khai báo công việc hàng ngày
- ⏰ Lập lịch khai báo theo giờ
- 📅 Khai báo tự động theo ngày trong tuần
- 💾 Lưu trữ thông tin đăng nhập
- 🔒 Bảo mật thông tin người dùng
- 🖥️ Chạy ẩn danh trong system tray

## Installation

1. Tải phiên bản mới nhất từ [Releases](https://github.com/ti014/SMBoard_Auto/releases/)
2. Tải file `SMBoardAuto.exe`

Hoặc build từ source code:

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Build ứng dụng
pyinstaller main.spec
```

**Usage**
1. Khai báo ngay lập tức
- Chọn tab "Tool"
- Chọn "Khai báo ngay lập tức"
- Nhấn "Start"
2. Khai báo theo giờ
- Chọn "Khai báo theo giờ"
- Nhập thời gian (HH:MM)
- Nhấn "Start"

3. Khai báo tự động theo ngày
- Chọn "Khai báo tự động theo giờ"
- Chọn các ngày trong tuần
- Nhập thời gian
- Nhấn "Start"

4. Để hủy lịch, vui lòng click chuột trái và chọn hủy:
![Cancel](/images/2.jpg)
## Requirements
- Windows 10/11
- Microsoft Edge Browser
- Python 3.10+ (nếu build từ source)
