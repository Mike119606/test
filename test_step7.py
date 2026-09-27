import sys
import time
import win32gui
import win32clipboard
import pyautogui
import logging

log_path = r"c:\Users\应轩旸\Documents\trae_projects\001\step7_test.txt"
log_file = open(log_path, "w", encoding="utf-8")
logging.basicConfig(stream=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
def log(msg):
    log_file.write(str(msg) + "\n")
    log_file.flush()

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.3

sys.path.insert(0, r"C:\Users\应轩旸\Desktop\WeChat-MCP-Server-main\src")
from wechat_controller import WeChatController

ctrl = WeChatController()

hwnd = ctrl._find_wechat_window()
ctrl._activate_window(hwnd)
log("1: activated")

# Search contact
pyautogui.hotkey('ctrl', 'f')
time.sleep(1.0)
pyautogui.hotkey('ctrl', 'a')
time.sleep(0.2)
pyautogui.press('delete')
time.sleep(0.2)
log("2: search box cleared")

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
time.sleep(0.25)
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.6)
log("3: pasted contact")

pyautogui.press('enter')
time.sleep(1.0)
log("4: search enter")

if orig:
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(orig, win32clipboard.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()

# Click input box - try multiple positions
rect = win32gui.GetWindowRect(hwnd)
wl, wt, wr, wb = rect
ww = wr - wl
positions = [
    (int(wl + ww // 2), int(wb - 80)),
    (int(wl + ww // 2), int(wb - 120)),
    (int(wl + ww // 3), int(wb - 100)),
]
log(f"5: trying positions, rect={rect}")

for i, (cx, cy) in enumerate(positions):
    log(f"5.{i}: click ({cx}, {cy})")
    try:
        pyautogui.click(cx, cy)
        time.sleep(0.4)
        # Try typing to verify focus
        pyautogui.typewrite('a')
        time.sleep(0.1)
        pyautogui.press('backspace')
        time.sleep(0.1)
        log(f"5.{i}: clicked and typed OK")
        break
    except Exception as e:
        log(f"5.{i}: EXCEPTION {e}")

log("6: input box clicked")

# Paste message
log("6a: ctrl+a")
try:
    pyautogui.hotkey('ctrl', 'a')
    log("6a: done")
except Exception as e:
    log(f"6a: EXCEPTION {e}")

time.sleep(0.12)
log("6b: sleep done")

log("6c: press delete")
try:
    pyautogui.press('delete')
    log("6c: done")
except Exception as e:
    log(f"6c: EXCEPTION {e}")

time.sleep(0.25)
log("6d: sleep done")

log("6e: clipboard")
try:
    win32clipboard.OpenClipboard()
    log("6e: opened")
    orig2 = None
    try:
        orig2 = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    except:
        pass
    log(f"6e: orig2={orig2!r}")
    win32clipboard.EmptyClipboard()
    log("6e: emptied")
    win32clipboard.SetClipboardText("测试成功", win32clipboard.CF_UNICODETEXT)
    log("6e: set")
    win32clipboard.CloseClipboard()
    log("6e: closed")
except Exception as e:
    log(f"6e: EXCEPTION {e}")
    try: win32clipboard.CloseClipboard()
    except: pass

time.sleep(0.25)
log("6f: sleep done")

log("6g: ctrl+v")
try:
    pyautogui.hotkey('ctrl', 'v')
    log("6g: done")
except Exception as e:
    log(f"6g: EXCEPTION {e}")

time.sleep(0.6)
log("6h: sleep done")

log("7: press enter")
try:
    pyautogui.press('enter')
    log("7: done")
except Exception as e:
    log(f"7: EXCEPTION {e}")

time.sleep(0.6)
log("DONE")
log_file.close()
