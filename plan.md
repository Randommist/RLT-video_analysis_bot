# План реализации: Бот для анализа видео

## Обзор архитектуры

Решение будет построено на Python 3.13 с использованием асинхронной архитектуры
для эффективной обработки обновлений Telegram и операций с базой данных.

- **Фреймворк бота**: `aiogram` (v3) для взаимодействия с Telegram.
- **База данных**: PostgreSQL (запуск через Docker).
- **ORM**: `Tortoise ORM` для асинхронного доступа к БД и определения моделей.
- **Конфигурация**: `pydantic-settings` для надежного управления переменными
  окружения.
- **Интеграция с LLM**: клиент `openai` (направленный на OpenRouter) для
  перевода естественного языка в SQL.

## Схема базы данных

На основе `videos-example.json` мы определим две основные модели:

### 1. `Video`

Хранит итоговую/текущую статистику видео.

- `id`: UUID (Первичный ключ)
- `creator_id`: Строка/UUID
- `video_created_at`: Datetime (Время оригинальной публикации)
- `views_count`: Int
- `likes_count`: Int
- `comments_count`: Int
- `reports_count`: Int
- `created_at`: Datetime (Системное время создания записи)
- `updated_at`: Datetime (Системное время обновления записи)

### 2. `VideoSnapshot`

Хранит почасовую статистику для отслеживания динамики.

- `id`: UUID (Первичный ключ)
- `video_id`: ForeignKey на `Video`
- `views_count`, `likes_count`, `comments_count`, `reports_count`: Int (Значения
  на момент снимка)
- `delta_views_count`, `delta_likes_count` и т.д.: Int (Изменения с момента
  последнего снимка)
- `created_at`: Datetime (Время снимка)
- `updated_at`: Datetime

## Стратегия LLM (Text-to-SQL)

Чтобы обеспечить точную генерацию SQL без "галлюцинаций", мы предоставим LLM
строгий системный промпт, содержащий:

1. **Роль**: Эксперт по PostgreSQL.
2. **Описание схемы**: Краткое DDL-описание таблиц `video` и `videosnapshot`.
3. **Ограничения**:
   - Возвращать **только** SQL-запрос (без markdown, без пояснений).
   - Запрос должен возвращать **одно числовое значение** (COUNT, SUM и т.д.).
   - Корректная обработка форматов дат (PostgreSQL `YYYY-MM-DD`).
4. **Примеры (Few-Shot)**: 2-3 примера пользовательских запросов, сопоставленных
   с правильным SQL.

## Структура проекта

```
.
├── docker-compose.yml   # Запуск PostgreSQL
├── Dockerfile           # Образ бота
├── .gitignore
├── pyproject.toml
├── README.md
└── video_analysis_bot/  # Основной код приложения
    ├── __init__.py
    ├── main.py          # Точка входа
    ├── config.py        # Настройки Pydantic
    ├── scripts/         # Скрипты
    │   └── load_data.py # ETL скрипт для загрузки JSON -> DB
    ├── db/
    │   ├── __init__.py
    │   └── models.py    # Модели Tortoise ORM
    ├── services/
    │   ├── __init__.py
    │   └── llm.py       # Логика взаимодействия с LLM
    └── handlers/
        ├── __init__.py
        └── bot.py       # Обработчики Telegram
```

## Пошаговый план реализации

1. **Инфраструктура**: Настройка `docker-compose.yml` для PostgreSQL.
2. **Конфигурация**: Реализация класса `Settings` в
   `video_analysis_bot/config.py`.
3. **База данных**: Определение моделей в `video_analysis_bot/db/models.py` и
   настройка логики инициализации.
4. **Загрузка данных**: Реализация `scripts/load_data.py` для парсинга
   `videos.json` и наполнения БД.
5. **Сервис LLM**: Реализация сборки промпта и вызова API в
   `video_analysis_bot/services/llm.py`.
6. **Логика бота**: Реализация обработчиков команд и текстовых сообщений в
   `video_analysis_bot/handlers/bot.py`.
   - Получение сообщения.
   - Генерация SQL через LLM.
   - Выполнение SQL через Tortoise/asyncpg.
   - Возврат результата.
7. **Тестирование**: Проверка на примерах запросов, предоставленных в задании.
8. **Документация**: Финализация `README.md`.
