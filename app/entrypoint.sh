#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    # если база еще не запущена
    echo "############################################ check DB"

    # Проверяем доступность хоста и порта
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.5
    done

    echo "############################################ DB = postgres. ok."
fi

#  Если надо удаляем все старые данные
# python manage.py flush --no-input

# Выполняем миграции
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --noinput

# python manage.py collectstatic  на будущее

# run pytest here
# pytest -s --showlocals

exec "$@"