import win32clipboard
import pyautogui
import time

log_path = r"c:\Users\应轩旸\Documents\trae_projects\001\clipboard_test.txt"
log_file = open(log_path, "w", encoding="utf-8")
def log(msg):
    log_file.write(str(msg) + "\n")
    log_file.flush()

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.3

log("1: open clipboard")
try:
    win32clipboard.OpenClipboard()
    log("2: opened")
    win32clipboard.EmptyClipboard()
    log("3: emptied")
    win32clipboard.SetClipboardText("test", win32clipboard.CF_UNICODETEXT)
    log("4: set text")
    win32clipboard.CloseClipboard()
    log("5: closed")
except Exception as e:
    log(f"CLIPBOARD ERROR: {e}")
    import traceback
    log(traceback.format_exc())

log("6: sleep")
time.sleep(0.25)

log("7: ctrl+v")
try:
    pyautogui.hotkey('ctrl', 'v')
    log("8: done")
except Exception as e:
    log(f"HOTKEY ERROR: {e}")

log("9: sleep")
time.sleep(0.6)

log("DONE")
log_file.close()
