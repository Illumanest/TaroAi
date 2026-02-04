import asyncio
import random
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import google.generativeai as genai  # Возвращаемся к классике

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = "8557375398:AAF0rafVTVUQmT7fUn68L0afBYOKW8NxsjM"
GEMINI_API_KEY = "AIzaSyBkPmLLkBiU5nA2CV3Y7wgIknDqFj-wJHU"
SERVICE_URL = "https://t.me/Natalya_Golovickaya"

# Настройка старым способом
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    for i in range(1, 4):
        builder.button(text=f"Расклад на {i} к.", callback_data=f"draw_{i}")
    await message.answer("🔮 Выберите количество карт:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("draw_"))
async def process_draw(callback: types.CallbackQuery):
    num = int(callback.data.split("_")[1])
    cards = ["Маг", "Луна", "Солнце", "Мир", "Сила", "Смерть", "Звезда", "Шут"]
    selected = random.sample(cards, num)
    cards_text = ", ".join(selected)
    
    await callback.message.answer(f"🔮 Выпали: {cards_text}\n⌛ ИИ расшифровывает...")

    try:
        # Старый, добрый и надежный метод
        response = model.generate_content(f"Ты таролог. Дай краткое предсказание по картам: {cards_text}")
        
        builder = InlineKeyboardBuilder()
        builder.button(text="Записаться", url=SERVICE_URL)
        
        await callback.message.answer(f"📜 Ответ:\n\n{response.text}", reply_markup=builder.as_markup())
    except Exception as e:
        print(f"ОШИБКА: {e}")
        await callback.message.answer(f"❌ Ошибка: {str(e)[:50]}")

# --- СЕРВЕР ДЛЯ RENDER ---
async def handle(request): return web.Response(text="OK")
async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
    asyncio.create_task(site.start())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
