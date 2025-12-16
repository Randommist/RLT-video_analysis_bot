import json
from openai import AsyncOpenAI
from config import settings

client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
)

SYSTEM_PROMPT = """
Ты — эксперт по PostgreSQL. Твоя задача — переводить вопросы на естественном языке в SQL-запросы.

Схема базы данных:
1. Table `videos` (итоговая статистика видео):
   - id (uuid, pk)
   - creator_id (varchar)
   - video_created_at (timestamp) -- дата публикации видео
   - views_count (int) -- просмотры
   - likes_count (int) -- лайки
   - comments_count (int) -- комментарии
   - reports_count (int) -- жалобы

2. Table `video_snapshots` (почасовая динамика):
   - id (uuid, pk)
   - video_id (uuid, fk -> videos.id)
   - created_at (timestamp) -- время замера (снапшота)
   - delta_views_count (int) -- прирост просмотров за час
   - delta_likes_count (int) -- прирост лайков
   - ... (остальные delta_ поля)

Правила:
1. Возвращай ТОЛЬКО SQL-запрос. Никакого markdown, никаких объяснений.
2. Запрос должен возвращать РОВНО ОДНО число (COUNT, SUM, MAX и т.д.).
3. Если спрашивают про "всего видео", используй `COUNT(*)` из таблицы `videos`.
4. Если спрашивают про "прирост" или "динамику" за конкретную дату, используй таблицу `video_snapshots` и суммируй `delta_...` поля.
5. Для фильтрации по датам используй `video_created_at` (для самих видео) или `created_at` (для снапшотов).
6. Учитывай, что даты в вопросе могут быть неточными, приводи их к формату 'YYYY-MM-DD'.
7. "С 1 по 5 ноября включительно" означает `>= '2025-11-01 00:00:00' AND <= '2025-11-05 23:59:59'`.

Примеры:
Q: Сколько всего видео есть в системе?
A: SELECT COUNT(*) FROM videos;

Q: Сколько видео у креатора '123' вышло с 1 ноября 2025?
A: SELECT COUNT(*) FROM videos WHERE creator_id = '123' AND video_created_at >= '2025-11-01';

Q: На сколько просмотров в сумме выросли все видео 28 ноября 2025?
A: SELECT SUM(delta_views_count) FROM video_snapshots WHERE created_at >= '2025-11-28 00:00:00' AND created_at <= '2025-11-28 23:59:59';
"""


async def generate_sql_query(user_text: str) -> str:
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.0,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM returned empty response")

    # Clean up markdown if present (prophylactic)
    cleaned_sql = content.replace("```sql", "").replace("```", "").strip()
    return cleaned_sql
