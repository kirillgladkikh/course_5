# Базовый образ с Python 3.13
FROM python:3.13-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы зависимостей Poetry
COPY pyproject.toml poetry.lock ./

# Устанавливаем системные зависимости (для psycopg2 и других пакетов)
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Устанавливаем зависимости проекта через Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

# Копируем весь код проекта в контейнер (после установки зависимостей)
COPY . .

# Создаём статические файлы и медиа‑директории
RUN mkdir -p static media

# Определяем переменные окружения
# Здесь указаны заглушки
# Реальные значения (при ручном запуске) будут переданы через команду docker run -e ...
ENV SECRET_KEY="my_secret_key"
ENV DEBUG=True
ENV DATABASE_NAME="my_database_name"
ENV DATABASE_USER="my_database_user"
ENV DATABASE_PASSWORD="my_database_password"
ENV DATABASE_HOST="my_database_host"
ENV DATABASE_PORT="my_database_port"
ENV TELEGRAM_TOKEN="my_telegram_token"
ENV CELERY_BROKER_URL="my_secret_key"
ENV CELERY_RESULT_BACKEND="my_celery_backend"

# Открываем порт, на котором будет работать Django
EXPOSE 8000

# Команда по умолчанию.
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
