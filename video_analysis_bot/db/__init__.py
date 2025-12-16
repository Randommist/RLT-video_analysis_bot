from tortoise import Tortoise
from config import settings


async def init_db():
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": ["video_analysis_bot.db.models"]},
    )
    # Generate schemas is usually for dev/test, but useful here for quick setup
    await Tortoise.generate_schemas()


async def close_db():
    await Tortoise.close_connections()
