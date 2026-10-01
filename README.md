# Discord OwO Automation Bot

Hệ thống tự động gửi lệnh OwO (`owo`, `owoh`, `owob`) với cơ chế luân phiên 2 cửa sổ/tab Discord (Pipelined Cooldown Alternating) hỗ trợ cả **Windows** và **macOS**.

---

## 📦 Tải bản phát hành (Releases):
Bạn có thể tải trực tiếp file chạy đóng gói sẵn tại trang Releases của GitHub:
👉 **[Tải bản mới nhất (Releases)](https://github.com/GREYAFRICANBIRD/TheBlue/releases)**
* **🪟 Windows**: Tải `OwOBot-Windows.zip` (gồm file `show_discord_window.exe` và `config.json`).
* **🍎 macOS**: Tải `OwOBotMac-macOS.zip` (gồm app `OwOBotMac.app` và `config.json`).

---

## 🎯 Tính năng tự động kiểm tra `hnsr` & Dừng theo chỉ tiêu Today:

* Tự động gửi lệnh `hnsr` định kỳ theo tần suất cấu hình (`hnsr_frequency`).
* Phân tích phản hồi từ bot máy chủ: Quét mục **OwO count** và đọc chỉ số **Today**.
* Khi chỉ số **Today >= target_owo_today** (mặc định: `300`), bot sẽ phát âm báo và **dừng hẳn chương trình**.

### ⚙️ Các thông số cấu hình trong `config.json`:
* `"check_hnsr"`: `true` / `false` (Bật/tắt tính năng kiểm tra mục tiêu).
* `"hnsr_command"`: `"hnsr"` (Tên lệnh dùng để kiểm tra thống kê).
* `"hnsr_frequency"`: `20` (Tần suất: cứ sau mỗi 20 chu kỳ lệnh sẽ gửi lệnh kiểm tra 1 lần).
* `"target_owo_today"`: `300` (Chỉ tiêu OwO count Today cần đạt để dừng hẳn bot).
* `"check_hnsr_on_start"`: `true` (Kiểm tra ngay chu kỳ đầu tiên xem đã đạt 300 từ trước hay chưa).

---

## 🪟 Windows Version (`window_version/`)

* File mã nguồn: `show_discord_window.py`
* Sử dụng Windows UI Automation & Win32 API.
* Tự động điều khiển và luân phiên giữa 2 cửa sổ Chrome trên thanh Taskbar.
* Chạy trực tiếp qua `python show_discord_window.py` hoặc file thực thi `.exe`.

---

## 🍎 macOS Version (`mac_version/`)

* File mã nguồn: `show_discord_mac.py`
* Tương tác trực tiếp với **Google Chrome** qua AppleScript (`osascript`) bản địa của macOS.
* Tự động phát hiện các cửa sổ Chrome đang mở Discord.
* Gửi lệnh luân phiên gối đầu và tự động kiểm tra `hnsr` theo chỉ tiêu.
