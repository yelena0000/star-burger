#!/bin/bash
cd /opt/star-burger
git pull
docker-compose -f docker-compose.prod.yaml down
docker-compose -f docker-compose.prod.yaml up --build -d

docker cp $(docker-compose -f docker-compose.prod.yaml ps -q frontend):/app/bundles /opt/star-burger/bundles

docker-compose -f docker-compose.prod.yaml run backend python manage.py migrate
docker-compose -f docker-compose.prod.yaml exec backend python manage.py collectstatic --noinput

docker cp $(docker-compose -f docker-compose.prod.yaml ps -q backend):/app/staticfiles /opt/star-burger/staticfiles

sudo cp -r /opt/star-burger/bundles/* /var/www/frontend/
sudo cp -r /opt/star-burger/staticfiles/* /var/www/frontend/

sudo systemctl restart nginx