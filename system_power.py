# system_power.py
import asyncio
import subprocess
import ctypes
from livekit.agents import function_tool

# ---------- 🔐 Lock ----------
@function_tool
async def lock_pc() -> str:
    """💠 पीसी लॉक करो (WIN+L जैसा)"""
    await asyncio.to_thread(ctypes.windll.user32.LockWorkStation)
    return "🔐 पीसी लॉक हो गया."

# ---------- ⏻ Shutdown ----------
@function_tool
async def shutdown_pc(delay_sec: int = 0) -> str:
    """⏻ पीसी शटडाउन करो (delay_sec सेकंड बाद)"""
    cmd = ["shutdown", "/s", "/t", str(max(0, delay_sec))]
    subprocess.Popen(cmd, shell=False)
    return f"⏻ शटडाउन कमांड भेजा गया (t={delay_sec}s)."

# ---------- 🔁 Restart ----------
@function_tool
async def restart_pc(delay_sec: int = 0) -> str:
    """🔁 पीसी रिस्टार्ट करो (delay_sec सेकंड बाद)"""
    cmd = ["shutdown", "/r", "/t", str(max(0, delay_sec))]
    subprocess.Popen(cmd, shell=False)
    return f"🔁 रिस्टार्ट कमांड भेजा गया (t={delay_sec}s)."

# ---------- 🌙 Sleep ----------
@function_tool
async def sleep_pc() -> str:
    """🌙 पीसी को स्लीप में डालो"""
  
    try:
        subprocess.Popen(
            ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], shell=False
        )
        return "🌙 स्लीप कमांड भेजा गया."
    except Exception as e:
        return f"⚠️ स्लीप विफल: {e}"
