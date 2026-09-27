import sys
import subprocess
import time
import re
import random
import json
import os

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
        "max_interval": 3.0
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

config = load_config()

RATES = config.get("rates", {"owo": 0.96, "owoh": 0.75, "owob": 0.84})
MAX_COOLDOWNS = config.get("max_cooldowns", {"owo": 10.0, "owoh": 15.0, "owob": 15.0})
RANDOM_ORDER = config.get("random_order", True)
MAX_INTERVAL = config.get("max_interval", 3.0)

def normalize_text(text):
    text = re.sub(r'[\u200b-\u200d\ufeff]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def run_applescript(script):
    try:
        res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return ""

def play_alert_sound():
    try:
        for _ in range(5):
            subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"])
            time.sleep(0.1)
    except Exception:
        print("\a" * 5)

def get_chrome_discord_windows():
    """
    Returns a list of dicts: [{'id': win_id, 'title': tab_title}, ...]
    representing Chrome windows that contain Discord.
    """
    script = '''
    tell application "Google Chrome"
        set winList to ""
        repeat with w in windows
            set wId to (id of w as string)
            set wTitle to (title of active tab of w)
            set isDiscord to false
            if wTitle contains "Discord" or wTitle contains "discord" then
                set isDiscord to true
            else
                repeat with t in tabs of w
                    if (title of t contains "Discord") or (title of t contains "discord") then
                        set isDiscord to true
                        exit repeat
                    end if
                end repeat
            end if
            if isDiscord then
                set winList to winList & wId & ":::" & wTitle & "|||"
            end if
        end repeat
        return winList
    end tell
    '''
    raw_output = run_applescript(script)
    if not raw_output:
        return []
        
    windows = []
    items = raw_output.split("|||")
    for item in items:
        if ":::" in item:
            w_id, title = item.split(":::", 1)
            windows.append({"id": w_id.strip(), "title": title.strip()})
            
    # Sort stable by window id
    windows.sort(key=lambda w: w["id"])
    return windows

def activate_chrome_window(win_id):
    """
    Brings the target Chrome window to front and focuses the Discord tab if needed.
    """
    script = f'''
    tell application "Google Chrome"
        activate
        repeat with w in windows
            if (id of w as string) is "{win_id}" then
                set index of w to 1
                -- Check if active tab is discord, if not find and select discord tab
                set currentTitle to title of active tab of w
                if not (currentTitle contains "Discord" or currentTitle contains "discord") then
                    repeat with i from 1 to count of tabs of w
                        set t to item i of tabs of w
                        if (title of t contains "Discord" or title of t contains "discord") then
                            set active tab index of w to i
                            exit repeat
                        end if
                    end repeat
                end if
                exit repeat
            end if
        end repeat
    end tell
    '''
    run_applescript(script)
    time.sleep(0.3)

def check_captcha_on_active_window(win_id):
    """
    Checks if active tab title contains captcha alert keywords.
    """
    script = f'''
    tell application "Google Chrome"
        repeat with w in windows
            if (id of w as string) is "{win_id}" then
                return title of active tab of w
            end if
        end repeat
        return ""
    end tell
    '''
    title = run_applescript(script)
    norm = normalize_text(title)
    if "captcha" in norm or "real human" in norm:
        print(f"\n[ALERT] Captcha detected in window title: '{title}'")
        return True
    return False

def send_message_mac(text):
    """
    Simulates typing text into the focused Discord input box and pressing Return.
    """
    script = f'''
    tell application "System Events"
        keystroke "{text}"
        key code 36
    end tell
    '''
    run_applescript(script)

def execute_commands_for_window(commands, rates, max_interval, window_label):
    for i, cmd in enumerate(commands):
        rate = rates[cmd]
        if random.random() < rate:
            send_message_mac(cmd)
            print(f"[{time.strftime('%H:%M:%S')}] [{window_label}] Sent '{cmd}'")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] [{window_label}] Skipped '{cmd}'")
            
        if i < len(commands) - 1:
            cmd_sleep = random.uniform(1.0, max_interval)
            print(f"[{time.strftime('%H:%M:%S')}] [{window_label}] Sleeping {cmd_sleep:.2f}s between commands...")
            time.sleep(cmd_sleep)

def main_loop():
    print("========================================================")
    print(" Discord OwO Auto-Bot for macOS (Google Chrome)")
    print(" Pipelined Multi-Window Alternating Enabled")
    print(" Press Ctrl+C in this terminal to stop.")
    print("========================================================")
    
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
    window_ready_times = {} # win_id -> next_ready_timestamp
    window_turn_index = 0
    
    try:
        while True:
            windows = get_chrome_discord_windows()
            if not windows:
                print(f"[{time.strftime('%H:%M:%S')}] Không tìm thấy cửa sổ Discord nào trên Google Chrome. Thử lại sau 5s...")
                time.sleep(5)
                continue
                
            num_windows = len(windows)
            curr_idx = window_turn_index % num_windows
            target_window = windows[curr_idx]
            win_id = target_window["id"]
            window_label = f"Cửa sổ {curr_idx + 1}/{num_windows}"
            
            # Check if target window is still in cooldown
            now = time.time()
            next_ready = window_ready_times.get(win_id, 0)
            wait_for_this = next_ready - now
            
            if wait_for_this > 0:
                print(f"[{time.strftime('%H:%M:%S')}] {window_label} đang trong cooldown ({wait_for_this:.2f}s). Chờ để tiếp tục...")
                time.sleep(wait_for_this)
                
            print(f"\n========================================================")
            print(f"[{time.strftime('%H:%M:%S')}] Đang xử lý: {window_label} | ID: {win_id} | '{target_window['title'][:35]}...'")
            print(f"========================================================")
            
            cycle_start = time.time()
            activate_chrome_window(win_id)
            
            # Captcha check (except first run)
            if not is_first_cycle:
                if check_captcha_on_active_window(win_id):
                    print("🚨 Captcha phát hiện trên Discord! Phát âm báo và dừng lại...")
                    play_alert_sound()
                    sys.exit(0)
                    
            is_first_cycle = False
            
            commands = ["owo", "owoh", "owob"]
            if RANDOM_ORDER:
                random.shuffle(commands)
                print(f"[{time.strftime('%H:%M:%S')}] Thứ tự lệnh: {commands}")
                
            execute_commands_for_window(commands, rates, max_interval, window_label)
            
            # Calculate cooldown: at least 15.0s from cycle_start
            last_cmd = commands[-1]
            max_val = max_cooldowns[last_cmd]
            this_cooldown = random.uniform(15.0, max(15.0, max_val))
            window_ready_times[win_id] = cycle_start + this_cooldown
            
            print(f"[{time.strftime('%H:%M:%S')}] {window_label} hoàn tất. Đặt cooldown {this_cooldown:.2f}s.")
            
            # Check next window readiness
            next_idx = (window_turn_index + 1) % num_windows
            next_win = windows[next_idx]
            next_id = next_win["id"]
            next_label = f"Cửa sổ {next_idx + 1}/{num_windows}"
            
            time_until_next = window_ready_times.get(next_id, 0) - time.time()
            if time_until_next <= 0:
                print(f"[{time.strftime('%H:%M:%S')}] {next_label} đã sẵn sàng! Chuyển ngay sang {next_label}...")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Chuyển sang {next_label} (cần chờ {time_until_next:.2f}s cooldown của cửa sổ đó)...")
                
            window_turn_index += 1
            
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình bởi người dùng.")

if __name__ == "__main__":
    main_loop()
