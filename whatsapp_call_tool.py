# whatsapp_call_tool.py
import time
import pyautogui
from livekit.agents import function_tool

# सुरक्षा: माउस को स्क्रीन के टॉप‑लेफ्ट में ले जाने पर स्क्रिप्ट तुरन्त रुक जाएगी (PyAutoGUI failsafe)
pyautogui.FAILSAFE = True

def _human_delay(t=0.6):
    time.sleep(t)

def _focus_search_and_open_chat(query: str):
    # Ctrl+F से WhatsApp का सर्च बॉक्स फोकस करो
    pyautogui.hotkey('ctrl', 'f')
    _human_delay(0.35)
    # पहले से लिखा टेक्स्ट हो तो select‑all करके साफ करो
    pyautogui.hotkey('ctrl', 'a')
    _human_delay(0.15)
    pyautogui.typewrite(query)    # नाम/नंबर टाइप करो
    _human_delay(1.0)
    pyautogui.press('down')       # पहले रिजल्ट पर जाओ
    pyautogui.press('enter')      # चैट खोलो
    _human_delay(0.8)

def _click_icon(icon_paths: list[str]) -> bool:
    # लाइट/डार्क थीम – दोनों के लिए अलग‑अलग टेम्पलेट इमेज सपोर्ट
    for path in icon_paths:
        loc = pyautogui.locateCenterOnScreen(path, grayscale=True)
        if loc:
            pyautogui.click(loc.x, loc.y)
            return True
    return False

@function_tool
async def whatsapp_voice_call(contact: str) -> str:
    """🟢 बताए गए कॉन्टैक्ट पर WhatsApp वॉइस कॉल शुरू करो (Desktop ऐप)"""
    _focus_search_and_open_chat(contact)
    ok = _click_icon([
        "assets/wa_voice_light.png",   # अपनी स्क्रीन से लिए हुए आइकन के स्क्रीनशॉट रखें
        "assets/wa_voice_dark.png"
    ])
    if ok:
        return f"📞 वॉइस कॉल शुरू हो गई: {contact}"
    return "⚠️ वॉइस कॉल आइकन नहीं मिला—आइकन के स्क्रीनशॉट अपडेट करें या डिस्प्ले स्केलिंग 100% रखें।"

@function_tool
async def whatsapp_video_call(contact: str) -> str:
    """🟢 बताए गए कॉन्टैक्ट पर WhatsApp वीडियो कॉल शुरू करो (Desktop ऐप)"""
    _focus_search_and_open_chat(contact)
    ok = _click_icon([
        "assets/wa_video_light.png",   # अपनी स्क्रीन से लिए हुए आइकन के स्क्रीनशॉट रखें
        "assets/wa_video_dark.png"
    ])
    if ok:
        return f"🎥 वीडियो कॉल शुरू हो गई: {contact}"
    return "⚠️ वीडियो कॉल आइकन नहीं मिला—आइकन के स्क्रीनशॉट अपडेट करें या डिस्प्ले स्केलिंग 100% रखें।"







