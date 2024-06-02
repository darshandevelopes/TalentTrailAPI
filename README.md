Admin pass: 123
admin username: darshan

docker-compose run django python manage.py migrate
docker-compose run django python manage.py createsuperuser
docker-compose run django python manage.py collect-static
