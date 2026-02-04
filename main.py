import os
import asyncio
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F

# Конфигурация
genai.configure(api_key="AIzaSyBkPmLLkBiU5nA2CV3Y7wgIknDqFj-wJHU")
# Пробуем САМЫЙ стабильный вариант названия
model = genai.GenerativeModel('gemini-pro') 

bot = Bot(token="8557375398:AAF0rafVTVUQmT7fUn68L0afBYOKW8NxsjM")
dp = Dispatcher()

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("Я живой! Нажми на кнопку или напиши вопрос.")

@dp.message()
async def chat(message: types.Message):
    try:
        # Прямой вызов без лишних наворотов
        response = model.generate_content(message.text)
        await message.answer(response.text)
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

async def main():
    # На Render важно просто запустить пуллинг, если вебхуки не настроены
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

