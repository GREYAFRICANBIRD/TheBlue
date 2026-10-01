# Discord OwO Automation Bot

Hệ thống tự động gửi lệnh OwO (`owo`, `owoh`, `owob`) với cơ chế luân phiên 2 cửa sổ/tab Discord (Pipelined Cooldown Alternating) hỗ trợ cả **Windows** và **macOS**.

---

## 🎯 Tính năng mới: Tự động kiểm tra lệnh `hnsr` & Dừng theo chỉ tiêu Today

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

## 🍎 macOS Version (`mac_version/`)

### Cách hoạt động:
* Tương tác trực tiếp với **Google Chrome** qua AppleScript (`osascript`) bản địa của macOS.
* Tự động phát hiện các cửa sổ Chrome đang mở Discord.
* Gửi lệnh luân phiên gối đầu và tự động kiểm tra `hnsr` theo chỉ tiêu.

### Tải bản macOS `.app` tự động qua GitHub Actions:
Dự án đã tích hợp sẵn GitHub Actions workflow (`.github/workflows/build-mac.yml`):
1. Mỗi khi code được push lên GitHub, GitHub Actions sẽ tự động khởi động runner macOS để build file ứng dụng **`OwOBotMac.app`**.
2. Để tải về:
   * Vào tab **Actions** trên repository GitHub của bạn: [https://github.com/GREYAFRICANBIRD/TheBlue/actions](https://github.com/GREYAFRICANBIRD/TheBlue/actions)
   * Chọn lần chạy (run) mới nhất của workflow **Build macOS App**.
   * Cuộn xuống phần **Artifacts** và tải về file **`OwOBotMac-macOS.zip`**.
   * Giải nén và mở file `.app` để chạy.

---

## 🪟 Windows Version (`gui_version/`)

* Sử dụng Windows UI Automation & Win32 API.
* Tự động điều khiển và luân phiên giữa 2 cửa sổ Chrome trên thanh Taskbar.
* Chạy trực tiếp qua `show_discord_gui.py` hoặc file thực thi `.exe` trong thư mục `TheRed/`.
