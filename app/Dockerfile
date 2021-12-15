# образ на основе которого создаём контейнер
FROM python:3.8.10-alpine3.14

# рабочая директория внутри проекта
WORKDIR /usr/src/app

# переменные окружения для python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем зависимости для Postgre
# не забываем использовать FROM .... -alpine3.14, иначе <apt-get> вместо apk и немного другой синтаксис
# v1
# RUN apk update \
#     && apk add postgresql-dev gcc python3-dev musl-dev

# v2
# мы пытаемся сделать тоже самое что и в v1, но некоторые пакеты нам нужны лишь
# для установки, а потом мы их можем снести
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \ 
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

# устанавливаем зависимости
RUN pip install --upgrade pip
COPY ./requirements.txt .
# ЗАЧЕМ ТОЧКА ПОСЛЕ txt?

# RUN pip install -r requirements.txt можно и так
# какой-то умный человек сказал так лучше всего:
RUN PYTHONPATH=/usr/bin/python pip install -r requirements.txt

# v2  подчищаем ненужное, минимизируя вес докеров
RUN apk del .tmp-build-deps

# копируем содержимое текущей папки в контейнер
COPY . .

# добавим запуск скрипта entrypoint.sh при запуске контейнера:
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
