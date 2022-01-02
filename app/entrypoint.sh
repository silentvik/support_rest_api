#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "# check DB"

    # Check the availability of the host and port
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "# DB = postgres. All is ok."
fi

# If necessary, delete all the old data
if [[ $ENTRYPOINT_FLUSH_DB = 1 ]]
then 
    echo "run FLUSH DB."
    python manage.py flush --no-input
fi

# If migrations have not been made and chosen in .env.dev
if [[ $ENTRYPOINT_MAKE_MIGRATIONS = 1 ]]
then
    echo "run MAKEMIGRATIONS."
    python manage.py makemigrations;
else
    echo "NO MAKEMIGRATIONS.";
fi

# Performing migrations
echo "run MIGRATE."
python manage.py migrate

# Another options from .env.dev
if [ $DJANGO_SUPERUSER_USERNAME ] && [ $DJANGO_SUPERUSER_EMAIL ] && [ $DJANGO_SUPERUSER_PASSWORD ]
then
  printenv | grep DJANGO_SUPERUSER_USERNAME
  printenv | grep DJANGO_SUPERUSER_EMAIL
  printenv | grep DJANGO_SUPERUSER_PASSWORD
  python manage.py createsuperuser --noinput
else
  echo "default DJANGO_SUPERUSER wasnt set"
fi

if [ $TICKETS_COLLECTOR_USERNAME ] && [ $TICKETS_COLLECTOR_EMAIL ] && [ $TICKETS_COLLECTOR_PASSWORD ]
then
    printenv | grep TICKETS_COLLECTOR_USERNAME
    printenv | grep TICKETS_COLLECTOR_EMAIL
    printenv | grep TICKETS_COLLECTOR_PASSWORD
    python manage.py create_super_user --username $TICKETS_COLLECTOR_USERNAME --password $TICKETS_COLLECTOR_PASSWORD --noinput --email $TICKETS_COLLECTOR_EMAIL 
else
    echo "default TICKETS_COLLECTOR wasnt set"
fi

# If there is a desire to run tests right here
if [[ $ENTRYPOINT_RUN_TESTS = 1 ]]
then
    printenv | grep ENTRYPOINT_RUN_TESTS
    echo "RUN pytest -s --showlocals"
    pytest -s --showlocals
fi


exec "$@"