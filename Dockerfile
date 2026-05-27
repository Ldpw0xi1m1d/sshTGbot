FROM python:3.11-slim

WORKDIR /srvbot

# Копируем зависимости
COPY dependencies.txt .
RUN pip install --no-cache-dir -r dependencies.txt

# Копируем код и .env
COPY . .

# Запуск бота
CMD ["python", "srvbot.py"]