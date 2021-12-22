# образ на основе которого создаём контейнер
FROM python:3.8.10-alpine3.14

# рабочая директория внутри проекта
WORKDIR /usr/src/app

# переменные окружения для python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем зависимости для Postgre
# некоторые пакеты нам нужны лишь
# для установки, а потом мы их можем снести**
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \ 
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

# устанавливаем зависимости
RUN pip install --upgrade pip
COPY ./requirements.txt .

# какой-то умный человек сказал так лучше всего:
RUN PYTHONPATH=/usr/bin/python pip install -r requirements.txt

# **подчищаем ненужное, минимизируя вес докеров
RUN apk del .tmp-build-deps

# копируем содержимое текущей папки в контейнер
COPY . .

# добавим запуск скрипта entrypoint.sh при запуске контейнера:
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
