import ctypes
import ctypes.wintypes as wt

user32 = ctypes.windll.user32
hits = []

@ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def cb(hwnd, lparam):
    if user32.IsWindowVisible(hwnd):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        t = buf.value
        if ('微信' in t) or ('WeChat' in t):
            # 过滤掉微信内置浏览器/小程序等子窗口，只要主窗口类
            cls = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, cls, 256)
            hits.append((hwnd, t, cls.value))
    return True

user32.EnumWindows(cb, 0)
for hwnd, title, cls in hits:
    print(f"hwnd={hwnd} class={cls} title={title!r}")
if not hits:
    print("NO_WINDOW")
