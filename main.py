import asyncio
import random
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from google import genai  # Импорт НОВОЙ библиотеки

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = "8557375398:AAF0rafVTVUQmT7fUn68L0afBYOKW8NxsjM"
GEMINI_API_KEY = "AIzaSyBkPmLLkBiU5nA2CV3Y7wgIknDqFj-wJHU"
SERVICE_URL = "https://t.me/Natalya_Golovickaya"  # Ссылка на провайдера услуг

# Инициализация нового клиента Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.button(text=f"Расклад на {i} к.", callback_data=f"draw_{i}")
    builder.adjust(2)
    await message.answer("🔮 Выберите количество карт:", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("draw_"))
async def process_draw(callback: types.CallbackQuery):
    num = int(callback.data.split("_")[1])
    cards_pool = ["Маг", "Дурак", "Смерть", "Солнце", "Луна", "Звезда", "Мир", "Сила", "Колесо Фортуны", "Отшельник"]
    selected_cards = random.sample(cards_pool, num)
    cards_text = ", ".join(selected_cards)

    await callback.message.answer(f"🔮 Вы вытянули: **{cards_text}**\n\n⌛ ИИ готовит ответ...")

    try:
        # НОВЫЙ способ вызова генерации текста
        response = client.models.generate_content(
            model="gemini-1.5-flash",  # Можно использовать последнюю версию
            contents=f"Ты таролог. Кратко расшифруй расклад: {cards_text}."
        )

        builder = InlineKeyboardBuilder()
        builder.button(text="Записаться", url=SERVICE_URL)

        await callback.message.answer(
            f"📜 **Предсказание:**\n\n{response.text}",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        await callback.message.answer("Ошибка связи с ИИ.")
        print(f"Ошибка: {e}")


# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="OK")


async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
    asyncio.create_task(site.start())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())