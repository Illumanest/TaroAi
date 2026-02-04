import asyncio, random, os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from google import genai
from google.genai import types as ai_types  # Важно для настроек безопасности

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = "8557375398:AAF0rafVTVUQmT7fUn68L0afBYOKW8NxsjM"
GEMINI_API_KEY = "AIzaSyBkPmLLkBiU5nA2CV3Y7wgIknDqFj-wJHU"
SERVICE_URL = "https://t.me/Natalya_Golovickaya"

client = genai.Client(api_key=GEMINI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


@dp.callback_query(F.data.startswith("draw_"))
async def process_draw(callback: types.CallbackQuery):
    num = int(callback.data.split("_")[1])
    cards = ["Маг", "Дурак", "Смерть", "Солнце", "Луна", "Звезда", "Мир", "Сила", "Дьявол", "Башня"]
    selected = random.sample(cards, num)
    cards_text = ", ".join(selected)

    await callback.message.answer(f"🔮 Карты: {cards_text}\n⌛ ИИ готовит ответ...")

    try:
        # Настраиваем конфиг: отключаем фильтры безопасности
        safe_config = ai_types.GenerateContentConfig(
            temperature=0.7,
            safety_settings=[
                ai_types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                ai_types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                ai_types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                ai_types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
            ]
        )

        response = client.models.generate_content(
            model="models/gemini-1.5-flash",
            contents=f"Ты профессиональный таролог. Дай краткую расшифровку расклада: {cards_text}",
            config=safe_config
        )

        # Проверка: если ИИ вернул пустой ответ (заблокировал сам себя)
        if not response.text:
            interpretation = "Звезды сегодня туманны... (ИИ заблокировал ответ по фильтрам безопасности)"
        else:
            interpretation = response.text

        builder = InlineKeyboardBuilder()
        builder.button(text="Записаться", url=SERVICE_URL)
        await callback.message.answer(f"📜 Предсказание:\n\n{interpretation}", reply_markup=builder.as_markup())

    except Exception as e:
        # ПЕЧАТАЕМ ПОЛНУЮ ОШИБКУ В ЛОГИ RENDER
        print(f"!!! КРИТИЧЕСКАЯ ОШИБКА ИИ: {str(e)}")
        await callback.message.answer(f"❌ Ошибка связи с ИИ. Причина: {str(e)[:50]}...")


# --- ВЕБ-СЕРВЕР ---
async def handle(request): return web.Response(text="OK")


async def main():
    app = web.Application();
    app.router.add_get('/', handle)
    runner = web.AppRunner(app);
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
    asyncio.create_task(site.start())
    await dp.start_polling(bot)



if __name__ == "__main__": asyncio.run(main())
