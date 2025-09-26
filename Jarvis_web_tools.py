# Jarvis_web_tools.py
import webbrowser
import asyncio
from livekit.agents import function_tool


@function_tool
async def website_kholo(site_name: str):
    """🌐 कोई भी वेबसाइट खोलो"""
    site_name = site_name.strip()
    if not site_name.startswith("http"):
        if "." not in site_name:
            site_name = "https://www." + site_name.lower().replace(" ", "") + ".com"
        else:
            site_name = "https://" + site_name
    await asyncio.to_thread(webbrowser.open, site_name)


@function_tool
async def youtube_kholo():
    """▶️ यूट्यूब खोलो"""
    await asyncio.to_thread(webbrowser.open, "https://www.youtube.com")


@function_tool
async def google_kholo():
    """🔎 गूगल खोलो"""
    await asyncio.to_thread(webbrowser.open, "https://www.google.com")
