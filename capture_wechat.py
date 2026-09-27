import sys
import time
import pyautogui
import logging

log_path = r"c:\Users\应轩旸\Documents\trae_projects\001\screenshot_log.txt"
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
log(f"hwnd={hwnd}")

if ctrl._activate_window(hwnd):
    log("activated")

# Take a screenshot of the WeChat window
import win32gui
rect = win32gui.GetWindowRect(hwnd)
log(f"rect={rect}")

time.sleep(0.5)
# Take full screen screenshot
img = pyautogui.screenshot()
img_path = r"c:\Users\应轩旸\Documents\trae_projects\001\wechat_screenshot.png"
img.save(img_path)
log(f"saved: {img_path}")

log("DONE")
log_file.close()
