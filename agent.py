# agent.py
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext, ChatMessage
from livekit.plugins import google, noise_cancellation

# Import your custom modules
from Jarvis_prompts import instructions_prompt, Reply_prompts
from Jarvis_google_search import google_search, get_current_datetime
from jarvis_get_whether import get_weather
from Jarvis_window_CTRL import open_app, close_app, folder_file
from Jarvis_file_opner import Play_file
from keyboard_mouse_CTRL import (
    move_cursor_tool, mouse_click_tool, scroll_cursor_tool,
    type_text_tool, press_key_tool, swipe_gesture_tool,
    press_hotkey_tool, control_volume_tool
)
from memory_loop import MemoryExtractor

load_dotenv()

# Media & Web Controls
from media_controls import toggle_play_pause, next_video, previous_video
from youtube_controls import video_search_karo, play_youtube
from Jarvis_web_tools import website_kholo, youtube_kholo, google_kholo

# System Controls
from system_controls import (
    get_volume, set_volume, change_volume,
    get_brightness, set_brightness, change_brightness,
)

# Power Controls
from system_power import lock_pc, shutdown_pc, restart_pc, sleep_pc

# Quick Actions
from system_quick_actions import bluetooth_set, energy_saver_on, energy_saver_off, night_light_set

# WhatsApp Tools
from whatsapp_reply_tool import whatsapp_smart_reply
from whatsapp_call_tool import whatsapp_voice_call, whatsapp_video_call

# Close all taskbar apps
from close_all_taskbar_apps import close_all_taskbar_apps

#PERSONAL INFO MANAGER ASYNC
from personal_info_manager_async import PersonalInfoManagerAsync



class Assistant(Agent):
    def __init__(self, chat_ctx) -> None:
        super().__init__(
            chat_ctx=chat_ctx,
            instructions=instructions_prompt,
            llm=google.beta.realtime.RealtimeModel(voice="Charon"),  # change voice if needed
            tools=[
                # Search & Info
                google_search,
                get_current_datetime,
                get_weather,

                # Apps & Files
                open_app,
                close_app,
                folder_file,
                Play_file,

                # Web & YouTube
                video_search_karo,
                play_youtube,
                website_kholo,
                youtube_kholo,
                google_kholo,

                # Media Controls
                toggle_play_pause,
                next_video,
                previous_video,

                # System Controls
                get_volume,
                set_volume,
                change_volume,
                get_brightness,
                set_brightness,
                change_brightness,

                # System Power
                lock_pc,
                shutdown_pc,
                restart_pc,
                sleep_pc,
                # Close all taskbar apps
                close_all_taskbar_apps,

                
            

                # Quick Actions
                bluetooth_set,
                energy_saver_on,
                energy_saver_off,
                night_light_set,

                # WhatsApp
                whatsapp_smart_reply,
                whatsapp_voice_call,
                whatsapp_video_call,

                # Keyboard & Mouse
                move_cursor_tool,
                mouse_click_tool,
                scroll_cursor_tool,
                type_text_tool,
                press_key_tool,
                press_hotkey_tool,
                control_volume_tool,
                swipe_gesture_tool,
            ]
        )


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(preemptive_generation=True)

    # Get current memory chat
    current_ctx = session.history.items

    await session.start(
        room=ctx.room,
        agent=Assistant(chat_ctx=current_ctx),  # send current chat to LLM in realtime
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await session.generate_reply(instructions=Reply_prompts)

    conv_ctx = MemoryExtractor()
    await conv_ctx.run(current_ctx)


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
# agent.py

# myenv\Scripts\activate
