import asyncio
import logging
import sys

try:
    from livekit.agents import function_tool
except ImportError:
    def function_tool(func): 
        return func







try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

# Encoding और Logger सेटअप
sys.stdout.reconfigure(encoding='utf-8') 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# विंडो फोकस करने का यूटिलिटी
# -------------------------
async def focus_window(title_keyword: str) -> bool:
    if not gw:
        logger.warning("⚠ pygetwindow लाइब्रेरी गायब है")
        return False

    await asyncio.sleep(1.5)  # विंडो खुलने का इंतज़ार
    title_keyword = title_keyword.lower().strip()

    for window in gw.getAllWindows():
        if title_keyword in window.title.lower():
            if window.isMinimized:
                window.restore()
            window.activate()
            return True
    return False

# -------------------------
# ऐप खोलने का फ़ंक्शन (Start Menu से)
# -------------------------
@function_tool()
async def open_app(app_title: str) -> str:
    """
    किसी भी ऐप को Start Menu से खोलो (path की ज़रूरत नहीं)।
    उदाहरण:
    - "open facebook"
    - "notepad खोलो"
    """
    app_title = app_title.lower().strip()

    try:
        if pyautogui:
            pyautogui.press("win")          # Start Menu खोलो
            await asyncio.sleep(1)
            pyautogui.typewrite(app_title)  # ऐप का नाम लिखो
            await asyncio.sleep(1.2)
            pyautogui.press("enter")        # एंटर दबाओ
            await asyncio.sleep(2)
            focused = await focus_window(app_title)
            return f"🚀 '{app_title}' खोला गया। Focus: {focused}"
        else:
            return "⚠ pyautogui लाइब्रेरी गायब है"
    except Exception as e:
        return f"❌ '{app_title}' खोलने में समस्या: {e}"

# -------------------------
# ऐप बंद करने का फ़ंक्शन
# -------------------------
closed_apps = []  # बंद हुए apps को ट्रैक करने के लिए

@function_tool()
async def close_app(window_title: str) -> str:
    """
    ऐप को उसके window title से बंद करो।
    उदाहरण:
    - "close notepad"
    - "chrome बंद करो"
    """
    if not win32gui:
        return "⚠ win32gui लाइब्रेरी गायब है"

    closed = []

    def enumHandler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if window_title.lower() in title.lower():
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                closed.append(title)
                closed_apps.append(window_title)  # रीओपन के लिए सेव करो

    win32gui.EnumWindows(enumHandler, None)

    if closed:
        return f"🛑 '{window_title}' बंद कर दिया गया।"
    else:
        return f"⚠ '{window_title}' नाम की कोई विंडो नहीं मिली।"

# -------------------------
# फ़ोल्डर या फ़ाइल खोलो
# -------------------------
@function_tool()
async def folder_file(path: str) -> str:
    """
    किसी भी फ़ोल्डर या फ़ाइल को Explorer में खोलो।
    उदाहरण:
    - "open downloads"
    - "folder D:\\Movies"
    """
    import os
    import subprocess

    try:
        if os.path.exists(path):
            subprocess.Popen(f'explorer "{path}"')
            return f"📂 '{path}' खोला गया।"
        else:
            return f"⚠ '{path}' मौजूद नहीं है।"
    except Exception as e:
        return f"❌ '{path}' खोलने में समस्या: {e}"

# -------------------------
# आखिरी बंद हुआ ऐप फिर से खोलो
# -------------------------
@function_tool()
async def reopen_last_app() -> str:
    """
    सबसे आखिरी बंद किए गए ऐप को फिर से खोलो।
    """
    if not closed_apps:
        return "⚠ कोई भी बंद हुआ ऐप नहीं मिला।"

    last_app = closed_apps[-1]  # आखिरी वाला ऐप
    msg = await open_app(last_app)
    return f"🔄 आखिरी बंद हुआ ऐप फिर से खोला गया: {last_app}\n{msg}"
