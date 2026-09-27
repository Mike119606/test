import sys
import time
import ctypes
import win32gui
import win32clipboard
import pyautogui
import logging

log_path = r"c:\Users\应轩旸\Documents\trae_projects\001\sendkeys_test.txt"
log_file = open(log_path, "w", encoding="utf-8")
logging.basicConfig(stream=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
def log(msg):
    log_file.write(str(msg) + "\n")
    log_file.flush()

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.3

# Use SendInput via ctypes for more stable key sending
user32 = ctypes.windll.user32
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
VK_RETURN = 0x0D
VK_DELETE = 0x2E
VK_A = 0x41
VK_V = 0x56
VK_F = 0x46

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
    """Press keys in order down, then reverse order up."""
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

ctrl = WeChatController()
hwnd = ctrl._find_wechat_window()
ctrl._activate_window(hwnd)
log("1: activated")

# Search contact
log("2: ctrl+f")
hotkey(VK_CONTROL, VK_F)
time.sleep(1.0)
log("2: done")

log("3: ctrl+a")
hotkey(VK_CONTROL, VK_A)
time.sleep(0.2)
log("3: done")

log("4: delete")
press_key(VK_DELETE)
time.sleep(0.2)
log("4: done")

# paste contact name
log("5: clipboard set")
win32clipboard.OpenClipboard()
orig = None
try:
    try:
        orig = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    except:
        pass
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText("文件传输助手", win32clipboard.CF_UNICODETEXT)
finally:
    win32clipboard.CloseClipboard()
log("5: done")

time.sleep(0.25)
log("6: ctrl+v")
hotkey(VK_CONTROL, VK_V)
time.sleep(0.6)
log("6: done")

log("7: enter")
press_key(VK_RETURN)
time.sleep(1.0)
log("7: done")

if orig:
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(orig, win32clipboard.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()

# Click input box
rect = win32gui.GetWindowRect(hwnd)
wl, wt, wr, wb = rect
ww = wr - wl
log(f"8: click input box, rect={rect}")
pyautogui.click(int(wl + ww // 2), int(wb - 80))
time.sleep(0.4)
log("8: done")

# paste message
log("9: ctrl+a")
hotkey(VK_CONTROL, VK_A)
time.sleep(0.12)
log("9: done")

log("10: delete")
press_key(VK_DELETE)
time.sleep(0.25)
log("10: done")

log("11: clipboard set msg")
win32clipboard.OpenClipboard()
orig2 = None
try:
    try:
        orig2 = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    except:
        pass
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText("测试成功", win32clipboard.CF_UNICODETEXT)
finally:
    win32clipboard.CloseClipboard()
log("11: done")

time.sleep(0.25)
log("12: ctrl+v")
hotkey(VK_CONTROL, VK_V)
time.sleep(0.6)
log("12: done")

log("13: enter (send)")
press_key(VK_RETURN)
time.sleep(0.6)
log("13: done")

if orig2:
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(orig2, win32clipboard.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()

log("DONE")
log_file.close()
