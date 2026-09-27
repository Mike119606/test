import sys
import time
import ctypes
import win32gui
import win32clipboard
import pyautogui
import logging

log_path = r"c:\Users\应轩旸\Documents\trae_projects\001\send_direct_log.txt"
log_file = open(log_path, "w", encoding="utf-8")
logging.basicConfig(stream=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
def log(msg):
    log_file.write(str(msg) + "\n")
    log_file.flush()

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.3

# Win32 SendInput for stable key sending
user32 = ctypes.windll.user32
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
VK_RETURN = 0x0D
VK_DELETE = 0x2E
VK_A = 0x41
VK_V = 0x56

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]
    _anonymous_ = ("_input",)
    _fields_ = [("type", ctypes.c_ulong), ("_input", _INPUT)]

def send_key(vk, up=False):
    extra = ctypes.pointer(ctypes.c_ulong(0))
    ii = INPUT()
    ii.type = INPUT_KEYBOARD
    ii.ki.wVk = vk
    ii.ki.wScan = 0
    ii.ki.dwFlags = KEYEVENTF_KEYUP if up else 0
    ii.ki.time = 0
    ii.ki.dwExtraInfo = extra
    user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(INPUT))

def hotkey(*keys):
    for k in keys:
        send_key(k, False)
        time.sleep(0.05)
    for k in reversed(keys):
        send_key(k, True)
        time.sleep(0.05)

def press_key(vk):
    send_key(vk, False)
    time.sleep(0.05)
    send_key(vk, True)
    time.sleep(0.05)

sys.path.insert(0, r"C:\Users\应轩旸\Desktop\WeChat-MCP-Server-main\src")
from wechat_controller import WeChatController

contact_name = sys.argv[1] if len(sys.argv) > 1 else "文件传输助手"
message = sys.argv[2] if len(sys.argv) > 2 else "测试成功"

ctrl = WeChatController()
hwnd = ctrl._find_wechat_window()
if not hwnd:
    log("ERROR: WeChat window not found")
    sys.exit(1)

if not ctrl._activate_window(hwnd):
    log("ERROR: failed to activate window")
    sys.exit(1)
log("1: window activated")

rect = win32gui.GetWindowRect(hwnd)
wl, wt, wr, wb = rect
ww = wr - wl
wh = wb - wt
log(f"2: rect={rect}, width={ww}, height={wh}")

# Step 3: Click "文件传输助手" in the left sidebar (middle area)
# Left sidebar X: around wl + 100 (within the sidebar)
# Y: middle of window, around wt + wh//2 (450px from top of window)
sidebar_x = int(wl + 100)
sidebar_y = int(wt + wh // 2)
log(f"3: clicking sidebar ({sidebar_x}, {sidebar_y})")
pyautogui.click(sidebar_x, sidebar_y)
time.sleep(1.0)
log("3: clicked")

# Step 4: Click input box (bottom area of window)
input_x = int(wl + ww // 2)
input_y = int(wb - 80)
log(f"4: clicking input box ({input_x}, {input_y})")
pyautogui.click(input_x, input_y)
time.sleep(0.5)
log("4: clicked")

# Step 5: Clear any existing text
log("5: ctrl+a")
hotkey(VK_CONTROL, VK_A)
time.sleep(0.12)
log("5: done")

log("6: delete")
press_key(VK_DELETE)
time.sleep(0.25)
log("6: done")

# Step 7: Set clipboard with message
log("7: clipboard set")
win32clipboard.OpenClipboard()
orig = None
try:
    try:
        orig = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    except:
        pass
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(message, win32clipboard.CF_UNICODETEXT)
finally:
    win32clipboard.CloseClipboard()
log("7: done")

time.sleep(0.25)

# Step 8: Paste message
log("8: ctrl+v")
hotkey(VK_CONTROL, VK_V)
time.sleep(0.6)
log("8: done")

# Step 9: Press enter to send
log("9: enter (send)")
press_key(VK_RETURN)
time.sleep(0.6)
log("9: done")

# Restore clipboard
if orig:
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(orig, win32clipboard.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()

log("DONE")
log_file.close()
