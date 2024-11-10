# Используем базовый образ Python
FROM python:3.9

# Устанавливаем рабочую директорию
WORKDIR /app

COPY ./src ./
COPY ./requirements.txt ./


# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем скрипт plot.py
CMD ["python", "plot.py"]
