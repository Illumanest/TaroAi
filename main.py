import os
import asyncio
from aiohttp import web
import google.generativeai as genai
from google.generativeai.types import RequestOptions
from aiogram import Bot, Dispatcher, types, F

# --- ТОЛЬКО САМОЕ ВАЖНОЕ ---
GEMINI_KEY = "AIzaSyBkPmLLkBiU5nA2CV3Y7wgIknDqFj-wJHU"
BOT_TOKEN = "8557375398:AAF0rafVTVUQmT7fUn68L0afBYOKW8NxsjM"

# Настройка ИИ с жестким указанием версии v1 (чтобы не было 404)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    request_options=RequestOptions(api_version='v1')
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработка любого текстового сообщения
@dp.message()
async def test_ai(message: types.Message):
    print(f"Пришел запрос: {message.text}")
    try:
        # Прямой запрос к модели
        response = model.generate_content(message.text)
        
        if response.text:
            await message.answer(f"🤖 Ответ ИИ:\n{response.text}")
        else:
            await message.answer("⚠️ ИИ вернул пустой ответ.")
            
    except Exception as e:
        error_text = str(e)
        print(f"Ошибка: {error_text}")
        await message.answer(f"❌ Ошибка: {error_text[:100]}")

# --- ФИКС ДЛЯ RENDER (Health Check) ---
async def handle(request):
    return web.Response(text="Бот работает")

async def main():
    # Запускаем веб-сервер, чтобы Render не убил процесс
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Порт берется из настроек Render автоматически
    port = int(os.getenv('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    asyncio.create_task(site.start())
    print(f"Тестовый бот запущен на порту {port}...")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

