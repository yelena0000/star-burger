#!/bin/bash
cd /opt/star-burger
git pull
docker-compose -f docker-compose.prod.yaml down
docker-compose -f docker-compose.prod.yaml up --build -d
docker-compose -f docker-compose.prod.yaml run backend python manage.py migrate
docker-compose -f docker-compose.prod.yaml run backend python manage.py collectstatic --noinput
sudo cp -r bundles/* /var/www/frontend/
sudo cp -r staticfiles/* /var/www/frontend/
sudo systemctl restart nginx