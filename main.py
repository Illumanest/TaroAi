import os
import asyncio
from aiohttp import web
import google.generativeai as genai
from google.generativeai.types import RequestOptions
from aiogram import Bot, Dispatcher, types

# Ключи
GEMINI_KEY = ""
BOT_TOKEN = "8557375398:AAF0rafVTVUQmT7fUn68L0afBYOKW8NxsjM"

# Настройка ИИ (версия v1 — лекарство от 404)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    request_options=RequestOptions(api_version='v1')
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def test_handler(message: types.Message):
    try:
        # Прямой запрос без настроек
        response = model.generate_content(message.text)
        await message.answer(f"✅ ИИ ответил:\n{response.text}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

# Заглушка для Render, чтобы он не выключал бота
async def handle(request): return web.Response(text="OK")

async def main():
    # Запускаем сервер на порту Render
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    port = int(os.getenv('PORT', 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()
    
    print(f"Бот запущен на порту {port}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

