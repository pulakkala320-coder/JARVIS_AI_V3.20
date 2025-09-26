# system_controls.py
import asyncio, shutil
from livekit.agents import function_tool

# ---------- Try C++ Module First ----------
_cpp_ok = False
try:
    import cpp_system_controls  # আমাদের compile করা pyd
    _cpp_ok = True
except Exception:
    _cpp_ok = False

# ---------- 🔊 Volume Controls ----------
if not _cpp_ok:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        _AUDIO_OK = True
    except Exception:
        _AUDIO_OK = False

    def _get_volume_obj():
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))

    def _get_volume_percent() -> int:
        vol = _get_volume_obj()
        scalar = vol.GetMasterVolumeLevelScalar()
        return int(round(scalar * 100))

    def _set_volume_percent(p: int):
        p = max(0, min(100, p))
        vol = _get_volume_obj()
        vol.SetMasterVolumeLevelScalar(p/100.0, None)

# ----------- Tools (volume) -----------

@function_tool
async def get_volume() -> str:
    """🔊 Get current system volume"""
    if _cpp_ok:
        return f"🔊 Volume is {cpp_system_controls.get_volume()}%."
    if not _AUDIO_OK:
        return "⚠️ PyCAW not available"
    val = await asyncio.to_thread(_get_volume_percent)
    return f"🔊 Volume is {val}%."

@function_tool
async def set_volume(percent: int) -> str:
    """🔊 Set volume directly to X%"""
    if _cpp_ok:
        cpp_system_controls.set_volume(percent)
        return f"✅ Volume set to {percent}%."
    if not _AUDIO_OK:
        return "⚠️ PyCAW not available"
    await asyncio.to_thread(_set_volume_percent, percent)
    cur = await asyncio.to_thread(_get_volume_percent)
    return f"✅ Volume set to {cur}%."

@function_tool
async def change_volume(delta: int) -> str:
    """🔊 Change volume by Δ%"""
    if _cpp_ok:
        cpp_system_controls.change_volume(delta)
        return f"🔊 Volume changed by {delta}%."
    if not _AUDIO_OK:
        return "⚠️ PyCAW not available"
    cur = await asyncio.to_thread(_get_volume_percent)
    newv = max(0, min(100, cur + delta))
    await asyncio.to_thread(_set_volume_percent, newv)
    return f"🔊 Changed, now {newv}%."

# ---------- 💡 Brightness Controls ----------
if not _cpp_ok:
    try:
        import screen_brightness_control as sbc
        _BR_OK = True
    except Exception:
        _BR_OK = False

    def _nircmd_available():
        return shutil.which("nircmd.exe") is not None

    def _get_brightness_percent() -> int:
        val = sbc.get_brightness()
        if isinstance(val, list):
            val = val[0]
        return int(val)

    def _set_brightness_percent(p: int):
        p = max(0, min(100, p))
        sbc.set_brightness(p)

# ----------- Tools (brightness) -----------

@function_tool
async def get_brightness() -> str:
    """💡 Get current brightness"""
    if _cpp_ok:
        return f"💡 Brightness is {cpp_system_controls.get_brightness()}%."
    if _BR_OK:
        val = await asyncio.to_thread(_get_brightness_percent)
        return f"💡 Brightness is {val}%."
    elif _nircmd_available():
        return "ℹ️ NirCmd available but no Python brightness lib."
    else:
        return "⚠️ Brightness control not available."

@function_tool
async def set_brightness(percent: int) -> str:
    """💡 Set brightness directly to X%"""
    if _cpp_ok:
        cpp_system_controls.set_brightness(percent)
        return f"✅ Brightness set to {percent}%."
    if _BR_OK:
        await asyncio.to_thread(_set_brightness_percent, percent)
        cur = await asyncio.to_thread(_get_brightness_percent)
        return f"✅ Brightness set to {cur}%."
    elif _nircmd_available():
        import subprocess
        p = max(0, min(100, percent))
        subprocess.Popen(["nircmd.exe", "setbrightness", str(p), "3"])
        return f"✅ (NirCmd) Brightness set to {p}%."
    else:
        return "⚠️ Brightness control not available."

@function_tool
async def change_brightness(delta: int) -> str:
    """💡 Change brightness by Δ%"""
    if _cpp_ok:
        cpp_system_controls.change_brightness(delta)
        return f"💡 Brightness changed by {delta}%."
    if _BR_OK:
        cur = await asyncio.to_thread(_get_brightness_percent)
        newp = max(0, min(100, cur + delta))
        await asyncio.to_thread(_set_brightness_percent, newp)
        return f"💡 Changed, now {newp}%."
    elif _nircmd_available():
        return "ℹ️ NirCmd mode: please specify direct percentage."
    else:
        return "⚠️ Brightness control not available."
