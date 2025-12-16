# Video Analysis Bot

Telegram-бот для аналитики видео на основе естественного языка. Бот преобразует
текстовые вопросы пользователя в SQL-запросы к базе данных PostgreSQL с помощью
LLM.

## Особенности

- **Естественный язык**: Понимает вопросы на русском языке (например, "Сколько
  просмотров было вчера?").
- **Text-to-SQL**: Использует LLM (через OpenRouter) для генерации безопасных
  SQL-запросов.
- **Асинхронность**: Полностью асинхронный стек (aiogram, tortoise-orm,
  asyncpg).
- **Docker**: Легкий запуск базы данных через Docker Compose.

## Требования

- Python 3.13+
- Docker & Docker Compose
- Ключ API OpenRouter (или OpenAI)
- Токен Telegram бота

## Установка и запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/Randommist/RLT-video_analysis_bot
   cd video_analysis_bot
   ```

2. **Создайте файл `.env`:** Скопируйте пример или создайте файл `.env` в корне
   проекта со следующим содержимым:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   OPENROUTER_API_KEY=your_openrouter_api_key

   # Опционально (значения по умолчанию):
   # POSTGRES_USER=user
   # POSTGRES_PASSWORD=password
   # POSTGRES_DB=video_analysis
   # POSTGRES_HOST=localhost
   # POSTGRES_PORT=5432
   # LLM_MODEL=google/gemini-2.5-flash
   ```

3. **Запустите базу данных:**
   ```bash
   docker-compose up -d
   ```

4. **Установите зависимости:** Рекомендуется использовать `uv` или `venv`:
   ```bash
   # Создание venv
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # .venv\Scripts\activate   # Windows

   # Установка зависимостей
   pip install -e .
   ```

5. **Загрузите данные:** Скрипт создаст таблицы и загрузит данные из
   `videos.json` (или другого файла).
   ```bash
   python scripts/load_data.py videos.json
   ```

6. **Запустите бота:**
   ```bash
   python video_analysis_bot/main.py
   ```

## Архитектура

- **`video_analysis_bot/`**: Основной пакет приложения.
  - **`config.py`**: Управление конфигурацией через переменные окружения.
  - **`db/`**: Модели данных (Tortoise ORM) и инициализация БД.
  - **`handlers/`**: Обработчики команд Telegram.
  - **`services/`**: Взаимодействие с LLM (генерация SQL).
- **`scripts/`**: Вспомогательные скрипты (загрузка данных).

### Схема данных

- **`Video`**: Содержит текущую/итоговую статистику по видео (просмотры, лайки и
  т.д.).
- **`VideoSnapshot`**: Содержит почасовые снимки статистики и дельты (изменения)
  показателей.

### Text-to-SQL

Бот использует системный промпт, описывающий схему базы данных, чтобы LLM могла
генерировать точные SQL-запросы. Запросы ограничиваются выборкой одного
числового значения.

## Тестирование

Для проверки бота используйте команду `/check` в служебном боте (см. задание).

Примеры вопросов:

- "Сколько всего видео есть в системе?"
- "На сколько просмотров в сумме выросли все видео 28 ноября 2025?"
