# media_controls.py
import asyncio
from livekit.agents import function_tool

try:
    import pyautogui
except ImportError:
    pyautogui = None


# ---------------------------
# Play / Pause toggle
# ---------------------------
@function_tool
async def toggle_play_pause() -> str:
    """⏯ YouTube वीडियो को play/pause टॉगल करेगा (space key)।"""
    if not pyautogui:
        return "⚠ pyautogui इंस्टॉल नहीं है।"
    try:
        pyautogui.press("space")
        return "⏯ play/pause किया गया।"
    except Exception as e:
        return f"❌ Error: {e}"


# ---------------------------
# Next Video
# ---------------------------
@function_tool
async def next_video() -> str:
    """⏭ YouTube पर अगला वीडियो चलाएगा (Shift + N)।"""
    if not pyautogui:
        return "⚠ pyautogui इंस्टॉल नहीं है।"
    try:
        pyautogui.hotkey("shift", "n")
        return "⏭ अगला वीडियो चलाया गया।"
    except Exception as e:
        return f"❌ Error: {e}"


# ---------------------------
# Previous Video
# ---------------------------
@function_tool
async def previous_video() -> str:
    """⏮ YouTube पर पिछला वीडियो चलाएगा (Shift + P)।"""
    if not pyautogui:
        return "⚠ pyautogui इंस्टॉल नहीं है।"
    try:
        pyautogui.hotkey("shift", "p")
        return "⏮ पिछला वीडियो चलाया गया।"
    except Exception as e:
        return f"❌ Error: {e}"
