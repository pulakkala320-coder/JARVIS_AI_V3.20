import psutil
import os
import signal
import asyncio

try:
    from livekit.agents import function_tool
except ImportError:
    def function_tool(func):
        return func


@function_tool()
async def close_all_taskbar_apps() -> str:
    """
    टास्कबार पर चल रहे सारे ऐप्स बंद करेगा (exclude list को छोड़कर)।
    उदाहरण:
    - "सारे ऐप्स बंद करो"
    - "close all taskbar apps"
    """
    exclude_list = ["explorer.exe", "python.exe", "System", "svchost.exe"]

    closed_apps = []
    tasks = []

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = proc.info['name']
            if pname and pname.lower() not in [e.lower() for e in exclude_list]:
                tasks.append(asyncio.to_thread(os.kill, proc.info['pid'], signal.SIGTERM))
                closed_apps.append(pname)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if tasks:
        await asyncio.gather(*tasks)

    if closed_apps:
        return f"🛑 ये ऐप्स बंद हो गए:\n{', '.join(closed_apps)}"
    else:
        return "⚠ कोई ऐप बंद नहीं हुआ।"
