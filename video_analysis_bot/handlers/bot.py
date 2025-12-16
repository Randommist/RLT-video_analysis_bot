from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from loguru import logger
from tortoise import Tortoise

from services.llm import generate_sql_query, DangerousWordError

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот-аналитик. Задай мне вопрос о статистике видео на естественном языке, и я постараюсь ответить числом.\n\n"
        "Примеры:\n"
        "- Сколько всего видео?\n"
        "- Сколько лайков набрали видео за вчера?\n"
    )


@router.message(F.text)
async def handle_text_query(message: Message):
    user_query = message.text
    if not user_query:
        return

    try:
        # 1. Generate SQL
        sql_query = await generate_sql_query(user_query)
        # await message.answer(f"DEBUG SQL: {sql_query}")  # Uncomment for debugging

        # 2. Execute SQL
        conn = Tortoise.get_connection("default")
        result = await conn.execute_query_dict(sql_query)

        # 3. Process Result
        # Expecting a single row with a single value, e.g. [{"count": 123}] or [{"sum": 500}]
        if not result or len(result) == 0:
            response_val = 0
        else:
            # Get the first value of the first row
            first_row = result[0]
            if not first_row:
                response_val = 0
            else:
                # We take the first value regardless of the key name
                response_val = list(first_row.values())[0]

                # Handle None (e.g. SUM of empty set)
                if response_val is None:
                    response_val = 0

        logger.info(
            f"User Query: {user_query} | Generated SQL: {sql_query} | Result: {response_val}"
        )
        await message.answer(str(response_val))

    except DangerousWordError as e:
        logger.warning(f"Security violation attempt: {user_query} | Error: {e}")
        await message.answer(
            "Действие запрещено: разрешены только запросы на чтение данных."
        )
    except Exception as e:
        logger.error(f"Error processing query '{user_query}': {e}")
        await message.answer(f"Произошла ошибка при обработке запроса: {str(e)}")
