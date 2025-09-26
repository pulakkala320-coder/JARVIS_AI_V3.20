# system_quick_actions.py  (हिंदी, डायनेमिक)
import asyncio, subprocess, webbrowser, shutil
from livekit.agents import function_tool

# =============== साझा हेल्पर ===============
def _run_ps(args: list[str]):
    """🔧 PowerShell कमांड चलाओ"""
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command"] + args,
        capture_output=True, text=True, timeout=25, shell=False
    )

def _run(cmd: list[str]):
    """🔧 बाहरी कमांड चलाओ"""
    return subprocess.run(cmd, capture_output=True, text=True, timeout=25, shell=False)

# =============== 🔵 Bluetooth ON/OFF ===============
# तरीका-1 (WinRT): Windows.Devices.Radios.Radio [On/Off]
_PS_BLUETOOTH = r"""
param([ValidateSet('On','Off')][string]$State)
if ((Get-Service bthserv).Status -eq 'Stopped') { Start-Service bthserv }
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? {
  $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
  $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
})[0]
function Await($op,[Type]$t){
  $netTask = ($asTaskGeneric.MakeGenericMethod($t)).Invoke($null, @($op))
  $netTask.Wait(-1) | Out-Null; $netTask.Result
}
[Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
[Windows.Devices.Radios.RadioAccessStatus,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
Await ([Windows.Devices.Radios.Radio]::RequestAccessAsync()) ([Windows.Devices.Radios.RadioAccessStatus]) | Out-Null
$radios = Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])
$bt = $radios | ? { $_.Kind -eq 'Bluetooth' }
[Windows.Devices.Radios.RadioState,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
Await ($bt.SetStateAsync($State)) ([Windows.Devices.Radios.RadioAccessStatus]) | Out-Null
"""

def _devcon_available() -> bool:
    return shutil.which("devcon.exe") is not None

async def _bluetooth_pnp_toggle(turn_on: bool) -> tuple[bool, str]:
    """Fallback: PowerShell PnPDevice (क्लास: Bluetooth)"""
    cmd = f"Get-PnpDevice -Class Bluetooth | {'Enable-PnpDevice' if turn_on else 'Disable-PnpDevice'} -Confirm:$false"
    ps = await asyncio.to_thread(_run_ps, [cmd])
    return (ps.returncode == 0), (ps.stdout or ps.stderr)

async def _bluetooth_devcon_toggle(turn_on: bool) -> tuple[bool, str]:
    """
    Fallback-2: DevCon (डिवाइस instance ID ऑटो-पिक करने की कोशिश)
    नोट: DevCon WDK से आता है; PATH में devcon.exe चाहिए।
    """
    if not _devcon_available():
        return False, "devcon.exe नहीं मिला"
    # सभी Bluetooth डिवाइस ढूंढो
    find = await asyncio.to_thread(_run, ["devcon.exe", "find", "*"])
    lines = (find.stdout or "").splitlines()
    bt_ids = [ln.split(":")[0].strip() for ln in lines if "Bluetooth" in ln]
    if not bt_ids:
        return False, "Bluetooth डिवाइस आईडी नहीं मिला"
    ok = True
    out_all = []
    for did in bt_ids:
        proc = await asyncio.to_thread(_run, ["devcon.exe", "enable" if turn_on else "disable", did])
        out_all.append(proc.stdout or proc.stderr or "")
        ok = ok and (proc.returncode == 0)
    return ok, "\n".join(out_all)

@function_tool
async def bluetooth_set(state: str) -> str:
    """🔵 ब्लूटूथ On/Off करो — state: 'on'/'off'"""
    turn_on = str(state).strip().lower() in {"on","1","enable","enabled","true","start"}
    desired = "On" if turn_on else "Off"

    # 1) WinRT स्क्रिप्ट
    ps = await asyncio.to_thread(_run_ps, ["-", _PS_BLUETOOTH, desired])
    if ps.returncode == 0:
        return f"✅ Bluetooth {desired} कर दिया गया."

    # 2) PnPDevice fallback (Admin चाहिए)
    ok, msg = await _bluetooth_pnp_toggle(turn_on)
    if ok:
        return f"✅ (PnP) Bluetooth {desired} कर दिया गया.\n{msg}"

    # 3) DevCon fallback (जरूरी हो तो)
    ok2, msg2 = await _bluetooth_devcon_toggle(turn_on)
    if ok2:
        return f"✅ (DevCon) Bluetooth {desired} कर दिया गया.\n{msg2}"

    return f"⚠️ Bluetooth {desired} विफल:\n{ps.stderr or ''}\n{msg}\n{msg2}"

# =============== ⚡ Energy Saver ON/OFF ===============
def _powercfg(args: list[str]):
    return subprocess.run(["powercfg"] + args, capture_output=True, text=True, timeout=15)

@function_tool
async def energy_saver_on() -> str:
    """⚡ एनर्जी सेवर चालू (DC threshold 100%)"""
    await asyncio.to_thread(_powercfg, ["/SETDCVALUEINDEX","SCHEME_CURRENT","SUB_ENERGYSAVER","ESBATTTHRESHOLD","100"])
    await asyncio.to_thread(_powercfg, ["/SETACTIVE","SCHEME_CURRENT"])
    return "✅ Energy Saver चालू हो गया (थ्रेशहोल्ड 100%)."

@function_tool
async def energy_saver_off() -> str:
    """⚡ एनर्जी सेवर बंद (DC threshold 0%)"""
    await asyncio.to_thread(_powercfg, ["/SETDCVALUEINDEX","SCHEME_CURRENT","SUB_ENERGYSAVER","ESBATTTHRESHOLD","0"])
    await asyncio.to_thread(_powercfg, ["/SETACTIVE","SCHEME_CURRENT"])
    return "✅ Energy Saver बंद हो गया (थ्रेशहोल्ड 0%)."

# =============== 🌙 Night light ON/OFF ===============
try:
    import pyautogui
    _GUI = True
except Exception:
    _GUI = False

def _wnl_call(on: bool) -> tuple[bool, str]:
    """यदि win-nightlight-cli (wnl.exe) PATH में है तो उसे चलाओ"""
    exe = shutil.which("wnl.exe")
    if not exe:
        return False, "wnl.exe उपलब्ध नहीं"
    p = subprocess.run([exe, "on" if on else "off"], capture_output=True, text=True, timeout=10)
    return (p.returncode == 0), (p.stdout or p.stderr)

@function_tool
async def night_light_set(state: str) -> str:
    """🌙 नाइट लाइट On/Off — state: 'on'/'off'"""
    on = str(state).strip().lower() in {"on","1","enable","enabled","true"}

    # 1) CLI हो तो
    ok, msg = await asyncio.to_thread(_wnl_call, on)
    if ok:
        return f"✅ Night light {'ON' if on else 'OFF'} कर दिया गया (wnl)."

    # 2) UI ऑटोमेशन (Settings → Night light)
    if _GUI:
        webbrowser.open("ms-settings:nightlight")
        await asyncio.sleep(1.2)
        await asyncio.to_thread(pyautogui.press, "space")  # टॉगल
        await asyncio.sleep(0.3)
        await asyncio.to_thread(pyautogui.hotkey, "alt", "f4")
        return "✅ Night light टॉगल कर दिया गया (UI)."

    return "⚠️ Night light टॉगल के लिए wnl.exe या pyautogui नहीं मिला."
