# whatsapp_reply_tool.py
import time
import pyautogui
from livekit.agents import function_tool

def human_delay(t=0.6):
    time.sleep(t)

@function_tool
async def whatsapp_smart_reply(search_term: str, message: str, hindi_mode: bool = False) -> str:
    """
    🟢 WhatsApp सक्रिय चैट खोजकर reply भेजो
    - पहले अंग्रेजी (या जैसा टाइप দিয়েছেন) দিয়ে सर्च करेगा।
    - अगर hindi_mode True है, तो देवना/हिंदी लिपि में इनपुट expect করবে।
    - नाम না मिले, fallback में बोले: 'नाम नहीं मिला, नंबर दें या हिंदी वर्तनी बोलें।'
    """

    # 1. सर्च फील्ड पर फोकस (Ctrl+F)
    pyautogui.hotkey('ctrl', 'f')
    human_delay(0.4)

    # 2. सर्च लिखो
    pyautogui.typewrite(search_term)
    human_delay(1.2)
    pyautogui.press("down")    # रिजल्ट पे जाओ
    pyautogui.press("enter")
    human_delay(0.7)

    # 3. चैट ओपन हुआ—मेसज भेजो
    try:
        pyautogui.typewrite(message)
        pyautogui.press("enter")
        return f"✅ '{search_term}' को WhatsApp मेसेज भेजा: {message}"
    except Exception as e:
        # 4. fallback: नाम/सर्च टर्म मिले न, तो वॉइस/GUI দিয়ে Hindi में दोबारा पूछ।
        if not hindi_mode:
            return "❓ नाम नहीं मिला। कृप्या हिंदी वर्तनी में बोले या नंबर दें।"
        else:
            return "❌ नंबर या नाम फिर भी नहीं मिला—मैनुअली WhatsApp ओपन करें।"
