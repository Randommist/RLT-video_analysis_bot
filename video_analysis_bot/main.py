import asyncio
import sys
from loguru import logger
from aiogram import Bot, Dispatcher
from config import settings
from handlers import bot as bot_handlers
from db import init_db, close_db


async def main():
    # Configure logging
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    # Initialize DB
    await init_db()

    # Initialize Bot and Dispatcher
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Register routers
    dp.include_router(bot_handlers.router)

    print("Bot started!")
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
