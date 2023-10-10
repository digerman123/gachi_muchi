import logging
import hashlib
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InputTextMessageContent, InlineQuery, InlineQueryResultArticle
import psycopg
from bot_config import TOKEN_API, DESCRIPTION, HELP_COMMANDS



# Налаштування логування та ініціалізація бота і диспетчера
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN_API)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Підключення до бази даних PostgreSQL
conn = psycopg.connect(
    dbname='postgres',
    user='postgres',
    password='qwerty',
    host='127.0.0.1'
)
cursor = conn.cursor()


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    await message.answer(DESCRIPTION)


@dp.message_handler(commands=['help'])
async def on_start(message: types.Message):
    await message.answer(HELP_COMMANDS)


@dp.message_handler(commands=['calc'])
async def on_calc(message: types.Message):
    try:
        _, gender, weight, height, age = message.text.split()
        weight = float(weight)
        height = float(height)
        age = int(age)

        if gender.lower() == "жінка":
            calories = (10 * weight) + (6.25 * height) - (5 * age) - 161
        elif gender.lower() == "чоловік":
            calories = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            await message.answer("Ви ввели некоректну стать. Введіть 'жінка' або 'чоловік'.")
            return

        await message.answer(f"Денна норма калорій: {calories} калорій")
    except ValueError:
        await message.answer("Некоректний формат введених даних. Використайте команду /calc [стать] [вага] [зріст] [вік]")


@dp.inline_handler()
async def search_products(inline_query: InlineQuery):
    query_text = inline_query.query

    # Виконуємо SQL-запит для пошуку продуктів у вашій таблиці
    cursor.execute("SELECT * FROM mytable WHERE name ILIKE %s", ['%' + query_text + '%'])
    results = cursor.fetchall()

    # Створюємо результати для інлайн-пошуку
    inline_results = []
    for result in results:
        result_id = hashlib.md5(result[0].encode()).hexdigest()
        item = InlineQueryResultArticle(
            id=result_id,  # Використовуємо унікальний result_id
            title=result[0],
            input_message_content=InputTextMessageContent(
                message_text=f"Назва: {result[0]}\nБілки: {result[1]}\nЖири: {result[2]}\nВуглеводи: {result[3]}\nКалорійність: {result[4]}"
            )
        )
        inline_results.append(item)

    await bot.answer_inline_query(inline_query_id=inline_query.id,
                                  results=inline_results,
                                  cache_time=1)



if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
