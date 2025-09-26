import json
import os
import aiofiles


class PersonalInfoManagerAsync:
    def __init__(self, file_path="personal_info.json"):
        self.file_path = file_path
        # अगर फाइल मौजूद नहीं है तो बना दें
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2, ensure_ascii=False)

    async def save_info(self, data: dict):
        """Async तरीके से personal info सेव करेगा"""
        async with aiofiles.open(self.file_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        print("✅ पर्सनल जानकारी सफलतापूर्वक सेव हो गई (async).")

    async def load_info(self) -> dict:
        """Async तरीके से personal info लोड करेगा"""
        async with aiofiles.open(self.file_path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)
