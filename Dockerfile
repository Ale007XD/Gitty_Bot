# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Метаданные
LABEL maintainer="Gitti Bot Team"
LABEL description="Telegram bot for learning guitar for kids"
LABEL version="1.0.0"

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя приложения для безопасности
RUN useradd -m -u 1000 gitti

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY app/requirements.txt .

# Обновляем pip и устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Создаем необходимые директории
RUN mkdir -p /app/logs /app/user_data && \
    chown -R gitti:gitti /app

# Копируем исходный код приложения
COPY app/ .

# Устанавливаем права доступа
RUN chown -R gitti:gitti /app

# Переключаемся на пользователя приложения
USER gitti

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('user_data') else 1)" || exit 1

# Указываем команду для запуска
CMD ["python", "-m", "bot.main"]
