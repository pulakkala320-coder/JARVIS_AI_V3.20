
# youtube_controls.py
import os
import asyncio
import webbrowser
import urllib.parse
import requests
from livekit.agents import function_tool

# -------------------------------------------
# 🔑 YouTube Data API endpoint
# -------------------------------------------
API_URL = "https://www.googleapis.com/youtube/v3/search"

# -------------------------------------------
# 🆔 पहले वीडियो का videoId निकालो (YouTube API से)
# -------------------------------------------
def _first_video_id(api_key: str, query: str) -> str | None:
    """
    👉 काम: दिए गए सर्च टेक्स्ट से पहला वीडियो ढूँढना और उसका videoId लौटाना
    ⚙️ तरीका: YouTube Data API (search.list) को कॉल करना
    """
    params = {
        "part": "snippet",          # कौन सा डेटा चाहिए
        "q": query,                 # क्या ढूँढना है
        "type": "video",            # सिर्फ वीडियो चाहिए
        "maxResults": 1,            # पहला रिज़ल्ट
        "regionCode": "IN",         # इंडिया रीज़न
        "safeSearch": "none",       # सेफ सर्च ऑफ
        "relevanceLanguage": "hi",  # हिंदी रिलेवेंस
        "key": api_key,             # 🔴 जरूरी: API key
    }
    r = requests.get(API_URL, params=params, timeout=10)
    r.raise_for_status()
    items = r.json().get("items", [])
    return items[0]["id"]["videoId"] if items else None

# -------------------------------------------
# 🔎 सिर्फ सर्च पेज खोलो (Fallback/Manual)
# -------------------------------------------
@function_tool
async def video_search_karo(query: str):
    """🔍 यूट्यूब पर कोई भी वीडियो खोजो (सर्च पेज खुलेगा)"""
    search = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={search}"
    await asyncio.to_thread(webbrowser.open, url)
    return f"🔎 '{query}' के लिए सर्च खोला गया।"

# -------------------------------------------
# ▶️ पहला वीडियो ऑटो‑प्ले करो (Watch URL)
# -------------------------------------------
@function_tool
async def play_youtube(query: str):
    """▶️ यूट्यूब पर पहला वीडियो चलाओ (ऑटो‑प्ले)"""
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()

    # अगर API key नहीं है तो सर्च पेज पर भेज दो
    if not api_key:
        search = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={search}"
        await asyncio.to_thread(webbrowser.open, url)
        return f"ℹ️ API key नहीं मिला, इसलिए सर्च खोला गया: '{query}'"

    # API से पहला videoId निकालो
    vid = await asyncio.to_thread(_first_video_id, api_key, query)
    if not vid:
        search = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={search}"
        await asyncio.to_thread(webbrowser.open, url)
        return f"⚠️ कोई वीडियो नहीं मिला, इसलिए सर्च खोला गया: '{query}'"

    # Direct watch URL खोलो ताकि तुरंत प्ले हो
    watch_url = f"https://www.youtube.com/watch?v={vid}"
    await asyncio.to_thread(webbrowser.open, watch_url)
    return f"🎵 '{query}' का पहला वीडियो अब चल रहा है।"
