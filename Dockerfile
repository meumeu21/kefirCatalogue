# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Создаем и переходим в рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Устанавливаем линтер (flake8)
RUN pip install flake8

# Запускаем линтер и проверяем код
RUN flake8 . --exclude=migrations --max-line-length=119

# Команда для запуска WSGI сервера (gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]