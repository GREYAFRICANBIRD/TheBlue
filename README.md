# Discord OwO Automation Bot

Hệ thống tự động gửi lệnh OwO (`owo`, `owoh`, `owob`) với cơ chế luân phiên 2 cửa sổ/tab Discord (Pipelined Cooldown Alternating) hỗ trợ cả **Windows** và **macOS**.

---

## 🍎 macOS Version (`mac_version/`)

### Cách hoạt động:
* Tương tác trực tiếp với **Google Chrome** qua AppleScript (`osascript`) bản địa của macOS.
* Tự động phát hiện các cửa sổ Chrome đang mở Discord.
* Thực hiện gửi lệnh luân phiên gối đầu: Trong khi cửa sổ 1 chờ cooldown 15s thì lập tức nhảy sang cửa sổ 2 để gửi lệnh, tối đa hóa hiệu suất cày bot.

### Tải bản macOS `.app` tự động qua GitHub Actions:
Dự án đã tích hợp sẵn GitHub Actions workflow (`.github/workflows/build-mac.yml`):
1. Mỗi khi code được push lên GitHub, GitHub Actions sẽ tự động khởi động runner macOS để build file ứng dụng **`OwOBotMac.app`**.
2. Để tải về:
   * Vào tab **Actions** trên repository GitHub của bạn.
   * Chọn lần chạy (run) mới nhất của workflow **Build macOS App**.
   * Cuộn xuống phần **Artifacts** và tải về file **`OwOBotMac-macOS.zip`**.
   * Giải nén và mở file `.app` để chạy.

---

## 🪟 Windows Version (`gui_version/`)

* Sử dụng Windows UI Automation & Win32 API.
* Tự động điều khiển và luân phiên giữa 2 cửa sổ Chrome trên thanh Taskbar.
* Chạy trực tiếp qua `show_discord_gui.py` hoặc file thực thi `.exe` trong thư mục `TheRed/`.
