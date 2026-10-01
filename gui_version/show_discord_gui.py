import sys
import subprocess
import time
import re
import winsound
import random
import json
import os
import ctypes
import tkinter as tk

# Ensure uiautomation is installed
try:
    import uiautomation as auto
except ImportError:
    print("Installing required library: uiautomation...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "uiautomation"])
    import uiautomation as auto

sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime, timedelta

SCRIPT_START_TIME = datetime.now()

CONFIG_FILE = "config.json"

def load_config():
    default_config = {
        "browser": "chrome",
        "rates": {
            "owo": 0.96,
            "owoh": 0.75,
            "owob": 0.84
        },
        "max_cooldowns": {
            "owo": 10.0,
            "owoh": 15.0,
            "owob": 15.0
        },
        "random_order": True,
        "max_interval": 3.0,
        "multi_window_mode": "alternate",
        "check_hnsr": True,
        "hnsr_command": "hnsr",
        "hnsr_frequency": 20,
        "target_owo_today": 300,
        "check_hnsr_on_start": True
    }
    
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
        return default_config
        
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] Failed to read '{CONFIG_FILE}': {e}")
        return default_config

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
    except Exception as e:
        print(f"[Error] Failed to save '{CONFIG_FILE}': {e}")

def choose_browser_gui():
    root = tk.Tk()
    root.title("Chọn Trình Duyệt")
    
    width = 320
    height = 140
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.resizable(False, False)
    root.configure(bg="#f5f5f5")
    
    browser_choice = [None]
    
    label = tk.Label(
        root, 
        text="Chọn trình duyệt chứa tab Discord của bạn:", 
        font=("Segoe UI", 10, "bold"), 
        bg="#f5f5f5", 
        fg="#333333",
        pady=15
    )
    label.pack()
    
    btn_frame = tk.Frame(root, bg="#f5f5f5")
    btn_frame.pack()
    
    def select_edge():
        browser_choice[0] = "edge"
        root.destroy()
        
    def select_chrome():
        browser_choice[0] = "chrome"
        root.destroy()
        
    btn_edge = tk.Button(
        btn_frame, 
        text="Microsoft Edge", 
        command=select_edge, 
        font=("Segoe UI", 9), 
        width=14, 
        height=1, 
        bg="#0078d4", 
        fg="white", 
        activebackground="#005a9e", 
        activeforeground="white",
        relief=tk.FLAT
    )
    btn_edge.pack(side=tk.LEFT, padx=10, pady=5)
    
    btn_chrome = tk.Button(
        btn_frame, 
        text="Google Chrome", 
        command=select_chrome, 
        font=("Segoe UI", 9), 
        width=14, 
        height=1, 
        bg="#ea4335", 
        fg="white", 
        activebackground="#d93025", 
        activeforeground="white",
        relief=tk.FLAT
    )
    btn_chrome.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def on_closing():
        root.destroy()
        sys.exit(0)
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    
    if browser_choice[0] is None:
        sys.exit(0)
        
    return browser_choice[0]

# Initial config load
config = load_config()

# If browser is not set, ask via GUI and save it to config.json
if not config.get("browser"):
    selected_browser = choose_browser_gui()
    config["browser"] = selected_browser
    save_config(config)

BROWSER_TYPE = config.get("browser", "chrome").lower()
RATES = config.get("rates", {"owo": 0.96, "owoh": 0.75, "owob": 0.84})
MAX_COOLDOWNS = config.get("max_cooldowns", {"owo": 10.0, "owoh": 15.0, "owob": 15.0})
RANDOM_ORDER = config.get("random_order", True)
MAX_INTERVAL = config.get("max_interval", 3.0)

# HNSR / Today Target configurations
CHECK_HNSR = config.get("check_hnsr", True)
HNSR_COMMAND = config.get("hnsr_command", "hnsr")
HNSR_FREQUENCY = max(1, config.get("hnsr_frequency", 20))
TARGET_OWO_TODAY = config.get("target_owo_today", 300)
CHECK_HNSR_ON_START = config.get("check_hnsr_on_start", True)

def normalize_text(text):
    text = re.sub(r'[\u200b-\u200d\ufeff]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def clean_text_for_parsing(text):
    t = re.sub(r'[\u200b-\u200d\ufeff]', '', text)
    t = re.sub(r'[*_`~>]', ' ', t)
    t = re.sub(r'[ \t]+', ' ', t)
    return t

def extract_today_count(full_text):
    clean = clean_text_for_parsing(full_text)
    
    # Priority 1: "owo count" block followed by "today" and digits
    pattern1 = r'owo\s*count[\s\S]*?today\s*[:\-\s]+(\d[\d,]*)'
    matches = re.findall(pattern1, clean, re.IGNORECASE)
    if matches:
        last_match = matches[-1]
        try:
            return int(last_match.replace(',', ''))
        except ValueError:
            pass
            
    # Priority 2: If "owo count" exists anywhere, find "today: <digits>"
    if re.search(r'owo\s*count', clean, re.IGNORECASE):
        matches2 = re.findall(r'today\s*[:\-\s]+(\d[\d,]*)', clean, re.IGNORECASE)
        if matches2:
            last_match = matches2[-1]
            try:
                return int(last_match.replace(',', ''))
            except ValueError:
                pass
                
    return None

def get_message_datetime(text):
    match = re.search(r'lúc\s+(\d{1,2}):(\d{2})[^,]*,\s*(\d{1,2})\s+tháng\s+(\d{1,2}),\s*(\d{4})', text)
    if match:
        try:
            hour, minute, day, month, year = map(int, match.groups())
            return datetime(year, month, day, hour, minute)
        except Exception:
            pass
    return None

def check_captcha_exists(window):
    has_captcha = [False]
    
    def check_control(control):
        if has_captcha[0]:
            return
        name = control.Name or ""
        norm_name = normalize_text(name)
        
        if "captcha" in norm_name or "real human" in norm_name or ("please" in norm_name and "link" in norm_name and "check" in norm_name):
            msg_time = get_message_datetime(name)
            if msg_time:
                if msg_time < SCRIPT_START_TIME - timedelta(minutes=5):
                    return
            
            print(f"\n[ALERT] New Captcha detected: '{name}'")
            has_captcha[0] = True
            return
            
        for child in control.GetChildren():
            check_control(child)
            
    check_control(window)
    return has_captcha[0]

def get_discord_chat_text(window):
    text_lines = []
    def collect_text(ctrl, depth=0):
        if depth > 35:
            return
        name = ctrl.Name
        if name and isinstance(name, str) and name.strip():
            text_lines.append(name.strip())
        for child in ctrl.GetChildren():
            collect_text(child, depth + 1)
    collect_text(window)
    return "\n".join(text_lines)

def check_hnsr_target(target_window, window_label):
    print(f"\n[{time.strftime('%H:%M:%S')}] [{window_label}] 🔍 Đang gửi lệnh kiểm tra '{HNSR_COMMAND}'...")
    auto.SendKeys(f'{HNSR_COMMAND}{{Enter}}')
    
    today_count = None
    # Wait for response (check after 2.0s and 3.5s)
    for attempt in range(2):
        time.sleep(2.0 if attempt == 0 else 1.5)
        chat_text = get_discord_chat_text(target_window)
        today_count = extract_today_count(chat_text)
        if today_count is not None:
            break
            
    if today_count is not None:
        print(f"[{time.strftime('%H:%M:%S')}] [{window_label}] 📊 Kết quả '{HNSR_COMMAND}': OwO count Today = {today_count} / {TARGET_OWO_TODAY}")
        if today_count >= TARGET_OWO_TODAY:
            print("\n" + "=" * 65)
            print(f"🎯 [HOÀN THÀNH MỤC TIÊU] OwO count Today đã đạt {today_count} (Chỉ tiêu: {TARGET_OWO_TODAY})!")
            print(f"🛑 Dừng hẳn chương trình theo đúng yêu cầu cấu hình.")
            print("=" * 65)
            for _ in range(4):
                winsound.Beep(1200, 350)
                time.sleep(0.1)
            sys.exit(0)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] [{window_label}] Chưa đạt mục tiêu ({today_count} < {TARGET_OWO_TODAY}). Tiếp tục chu kỳ...")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] [{window_label}] Chưa đọc được thông số Today từ '{HNSR_COMMAND}'. Tiếp tục chu kỳ...")
        
    time.sleep(random.uniform(1.0, 2.0))

def bring_window_to_front(hwnd):
    if not hwnd:
        return
    try:
        if ctypes.windll.user32.IsIconic(hwnd):
            ctypes.windll.user32.ShowWindow(hwnd, 9) # SW_RESTORE
        else:
            ctypes.windll.user32.ShowWindow(hwnd, 5) # SW_SHOW
            
        current_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        target_thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
        
        if current_thread_id != target_thread_id:
            ctypes.windll.user32.AttachThreadInput(current_thread_id, target_thread_id, True)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            ctypes.windll.user32.SetFocus(hwnd)
            ctypes.windll.user32.AttachThreadInput(current_thread_id, target_thread_id, False)
        else:
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            ctypes.windll.user32.SetFocus(hwnd)
    except Exception:
        pass

def find_all_discord_windows(browser_type):
    top_windows = auto.GetRootControl().GetChildren()
    matched_windows = []
    seen_handles = set()
    
    for window in top_windows:
        if window.ClassName == 'Chrome_WidgetWin_1':
            try:
                handle = window.NativeWindowHandle
                if not handle or handle in seen_handles:
                    continue
                
                process_name = ""
                try:
                    import psutil
                    process_name = psutil.Process(window.ProcessId).name().lower()
                except Exception:
                    pass
                
                is_browser = False
                if browser_type == "chrome":
                    is_browser = "chrome" in process_name or "chrome" in window.Name.lower()
                else:
                    is_browser = "msedge" in process_name or "edge" in window.Name.lower()
                
                if is_browser:
                    is_discord = "discord" in window.Name.lower()
                    
                    if not is_discord:
                        def has_discord_tab(ctrl, depth=0):
                            if depth > 10:
                                return False
                            if ctrl.ControlTypeName == 'TabItemControl' and 'discord' in ctrl.Name.lower():
                                return True
                            for child in ctrl.GetChildren():
                                if has_discord_tab(child, depth + 1):
                                    return True
                            return False
                        is_discord = has_discord_tab(window)
                    
                    if is_discord:
                        seen_handles.add(handle)
                        matched_windows.append(window)
            except Exception:
                continue
                
    # Sort stable by NativeWindowHandle (Window 1, Window 2 stay fixed)
    matched_windows.sort(key=lambda w: w.NativeWindowHandle)
    return matched_windows

def focus_and_prepare_window(window, skip_captcha=False):
    try:
        handle = window.NativeWindowHandle
        bring_window_to_front(handle)
        time.sleep(0.3)
        
        window.SetActive()
        window.SetFocus()
        
        # If there is a tab with "discord", click it (if it's a tabbed browser window)
        def find_discord_tab(control, depth=0):
            if depth > 10:
                return None
            if control.ControlTypeName == 'TabItemControl' and 'discord' in control.Name.lower():
                return control
            for child in control.GetChildren():
                res = find_discord_tab(child, depth + 1)
                if res:
                    return res
            return None

        discord_tab = find_discord_tab(window)
        if discord_tab:
            discord_tab.Click(simulateMove=False)
            time.sleep(0.1)

        # Check for captcha
        if not skip_captcha and check_captcha_exists(window):
            print(f"🚨 Captcha detected in window '{window.Name}'! Playing alert sound and stopping loop...")
            for _ in range(5):
                winsound.Beep(1000, 500)
                time.sleep(0.1)
            sys.exit(0)

        # Find the message box
        def find_message_box(control, depth=0):
            if depth > 35:
                return None
            if control.ControlTypeName == 'EditControl':
                name_lower = control.Name.lower()
                if ('nhắn' in name_lower or 'message' in name_lower) and 'địa chỉ' not in name_lower and 'tìm kiếm' not in name_lower:
                    return control
            for child in control.GetChildren():
                res = find_message_box(child, depth + 1)
                if res:
                    return res
            return None

        msg_box = find_message_box(window)
        if msg_box:
            msg_box.Click(simulateMove=False)
            time.sleep(0.1)
            return True
        else:
            window.SetFocus()
            return True
    except Exception as e:
        if isinstance(e, SystemExit):
            raise e
        print(f"[Error] Failed to focus window '{window.Name}': {e}")
        return False

def execute_commands_for_window(target_window, commands, rates, max_interval, window_label):
    for i, cmd in enumerate(commands):
        rate = rates[cmd]
        if random.random() < rate:
            auto.SendKeys(f'{cmd}{{Enter}}')
            print(f"[{time.strftime('%H:%M:%S')}] [{window_label}] Sent '{cmd}'")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] [{window_label}] Skipped '{cmd}'")
            
        if i < len(commands) - 1:
            cmd_sleep = random.uniform(1.0, max_interval)
            print(f"[{time.strftime('%H:%M:%S')}] [{window_label}] Sleeping {cmd_sleep:.2f}s between commands...")
            time.sleep(cmd_sleep)

def main_loop():
    print(f"Starting Multi-Window Discord Bot using {BROWSER_TYPE.upper()} (GUI Mode).")
    print("Chế độ: Luân phiên liên tục (Trong khi cửa sổ này cooldown, lập tức chuyển sang cửa sổ kia).")
    if CHECK_HNSR:
        print(f"Theo dõi mục tiêu: Lệnh '{HNSR_COMMAND}', tần suất mỗi {HNSR_FREQUENCY} chu kỳ, mục tiêu Today = {TARGET_OWO_TODAY}.")
    print("Press Ctrl+C in this terminal to stop.")
    
    rates = {
        "owo": RATES.get("owo", 0.96),
        "owoh": RATES.get("owoh", 0.75),
        "owob": RATES.get("owob", 0.84)
    }
    
    max_cooldowns = {
        "owo": max(1.0, MAX_COOLDOWNS.get("owo", 10.0)),
        "owoh": max(1.0, MAX_COOLDOWNS.get("owoh", 15.0)),
        "owob": max(13.0, MAX_COOLDOWNS.get("owob", 15.0))
    }
    
    max_interval = max(1.0, MAX_INTERVAL)
    is_first_cycle = True
    
    # Track when each window will finish its cooldown
    window_ready_times = {} # handle -> next_ready_timestamp
    window_cycle_counts = {} # handle -> cycle count
    window_turn_index = 0
    
    try:
        while True:
            windows = find_all_discord_windows(BROWSER_TYPE)
            if not windows:
                print(f"[{time.strftime('%H:%M:%S')}] Không tìm thấy cửa sổ Discord nào trên {BROWSER_TYPE.upper()}. Thử lại sau 5s...")
                time.sleep(5)
                continue
                
            num_windows = len(windows)
            curr_idx = window_turn_index % num_windows
            target_window = windows[curr_idx]
            handle = target_window.NativeWindowHandle
            window_label = f"Cửa sổ {curr_idx + 1}/{num_windows}"
            
            # Check if this target window is still in cooldown
            now = time.time()
            next_ready = window_ready_times.get(handle, 0)
            wait_for_this = next_ready - now
            
            if wait_for_this > 0:
                print(f"[{time.strftime('%H:%M:%S')}] {window_label} đang trong cooldown ({wait_for_this:.2f}s). Chờ để tiếp tục...")
                time.sleep(wait_for_this)
                
            print(f"\n========================================================")
            print(f"[{time.strftime('%H:%M:%S')}] Đang xử lý: {window_label} | HWND: {handle} | '{target_window.Name[:35]}...'")
            print(f"========================================================")
            
            cycle_start = time.time()
            
            if not focus_and_prepare_window(target_window, skip_captcha=is_first_cycle):
                print(f"Không thể kích hoạt {window_label}. Bỏ qua lượt này...")
                time.sleep(2)
                window_turn_index += 1
                continue
                
            is_first_cycle = False
            
            # Increment cycle count for this window
            window_cycle_counts[handle] = window_cycle_counts.get(handle, 0) + 1
            curr_cycles = window_cycle_counts[handle]
            
            # Periodic check for HNSR / Today target
            if CHECK_HNSR:
                should_check = (curr_cycles == 1 and CHECK_HNSR_ON_START) or (curr_cycles % HNSR_FREQUENCY == 0)
                if should_check:
                    check_hnsr_target(target_window, window_label)
            
            commands = ["owo", "owoh", "owob"]
            if RANDOM_ORDER:
                random.shuffle(commands)
                print(f"[{time.strftime('%H:%M:%S')}] Thứ tự lệnh: {commands}")
                
            execute_commands_for_window(target_window, commands, rates, max_interval, window_label)
            
            # Calculate cooldown for this window:
            # Must be at least 15.0s from cycle_start to satisfy OwO bot cooldown rules
            last_cmd = commands[-1]
            max_val = max_cooldowns[last_cmd]
            this_cooldown = random.uniform(15.0, max(15.0, max_val))
            window_ready_times[handle] = cycle_start + this_cooldown
            
            print(f"[{time.strftime('%H:%M:%S')}] {window_label} hoàn tất. Đặt cooldown {this_cooldown:.2f}s.")
            
            # Determine next window
            next_idx = (window_turn_index + 1) % num_windows
            next_window = windows[next_idx]
            next_handle = next_window.NativeWindowHandle
            next_label = f"Cửa sổ {next_idx + 1}/{num_windows}"
            
            time_until_next = window_ready_times.get(next_handle, 0) - time.time()
            if time_until_next <= 0:
                print(f"[{time.strftime('%H:%M:%S')}] {next_label} đã sẵn sàng! Chuyển ngay sang {next_label}...")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Chuyển sang {next_label} (cần chờ {time_until_next:.2f}s cooldown của cửa sổ đó)...")
                
            # Advance to next window
            window_turn_index += 1
            
    except KeyboardInterrupt:
        print("\nLoop stopped by user.")

if __name__ == "__main__":
    main_loop()
