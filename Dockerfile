# Используем базовый образ Python 3.11
FROM python:3.12-alpine

# Команда для вывода логов в консоле
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочий каталог
WORKDIR /all_inclusive

# Копируем файл requirements.txt
COPY requirements.txt requirements.txt

# Экспортируем порт, который будет использоваться для доступа к приложению
EXPOSE 8000

# Устанавливаем зависимости из файла requirements.txt без кэша
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы и папки из папки CRM_system в рабочий каталог WORKDIR
COPY all_inclusive .
