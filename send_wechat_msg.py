import sys
import time
import win32gui
import win32clipboard
import pyautogui
import logging

# Redirect logging to file
log_path = r"c:\Users\应轩旸\Documents\trae_projects\001\send_log.txt"
log_file = open(log_path, "w", encoding="utf-8")
logging.basicConfig(stream=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', force=True)

def log(msg):
    log_file.write(str(msg) + "\n")
    log_file.flush()

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.3

sys.path.insert(0, r"C:\Users\应轩旸\Desktop\WeChat-MCP-Server-main\src")
from wechat_controller import WeChatController

contact_name = sys.argv[1] if len(sys.argv) > 1 else "文件传输助手"
message = sys.argv[2] if len(sys.argv) > 2 else "测试成功"

ctrl = WeChatController()

# Step 1: find + activate window
hwnd = ctrl._find_wechat_window()
if not hwnd:
    log("ERROR: WeChat window not found")
    sys.exit(1)
log(f"1: found hwnd={hwnd}")

if not ctrl._activate_window(hwnd):
    log("ERROR: failed to activate window")
    sys.exit(1)
log("2: window activated")

# Step 2: search contact via Ctrl+F (works for general contacts)
pyautogui.hotkey('ctrl', 'f')
time.sleep(1.0)
pyautogui.hotkey('ctrl', 'a')
time.sleep(0.2)
pyautogui.press('delete')
time.sleep(0.2)
log("3: search box opened")

# paste contact name
win32clipboard.OpenClipboard()
orig = None
try:
    try:
        orig = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    except Exception:
        pass
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(contact_name, win32clipboard.CF_UNICODETEXT)
finally:
    win32clipboard.CloseClipboard()
time.sleep(0.25)
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.6)
log("4: pasted contact name")

pyautogui.press('enter')
time.sleep(1.0)
log("5: searched contact")

# restore clipboard
if orig:
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(orig, win32clipboard.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()

# Step 3: click input box
rect = win32gui.GetWindowRect(hwnd)
wl, wt, wr, wb = rect
ww = wr - wl
pyautogui.click(int(wl + ww // 2), int(wb - 80))
time.sleep(0.4)
log("6: clicked input box")

# Step 4: paste message
pyautogui.hotkey('ctrl', 'a')
time.sleep(0.12)
pyautogui.press('delete')
time.sleep(0.25)

win32clipboard.OpenClipboard()
orig2 = None
try:
    try:
        orig2 = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    except Exception:
        pass
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(message, win32clipboard.CF_UNICODETEXT)
finally:
    win32clipboard.CloseClipboard()
time.sleep(0.25)
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.6)
log("7: pasted message")

# Step 5: press enter to send
pyautogui.press('enter')
time.sleep(0.6)
log("8: message sent")

# restore clipboard
if orig2:
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(orig2, win32clipboard.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()

log("DONE: message sent successfully")
log_file.close()
