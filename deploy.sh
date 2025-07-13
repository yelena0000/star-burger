#!/bin/bash
cd /opt/star-burger
git pull

echo "[deploy] Очищаю временные папки..."
sudo rm -rf /opt/star-burger/bundles
sudo rm -rf /opt/star-burger/staticfiles
sudo rm -rf /var/www/frontend/*

docker-compose -f docker-compose.prod.yaml down
docker-compose -f docker-compose.prod.yaml up --build -d

echo "[deploy] Копирую бандлы из контейнера..."
docker cp $(docker-compose -f docker-compose.prod.yaml ps -q frontend):/app/bundles /opt/star-burger/bundles

echo "[deploy] Применяю миграции и собираю статику..."
docker-compose -f docker-compose.prod.yaml run backend python manage.py migrate
docker-compose -f docker-compose.prod.yaml exec backend python manage.py collectstatic --noinput

echo "[deploy] Копирую статику из контейнера..."
docker cp $(docker-compose -f docker-compose.prod.yaml ps -q backend):/app/staticfiles /opt/star-burger/staticfiles

echo "[deploy] Копирую файлы в /var/www/frontend..."
sudo cp -r /opt/star-burger/bundles/bundles/* /var/www/frontend/
sudo cp -r /opt/star-burger/staticfiles/staticfiles/* /var/www/frontend/

echo "[deploy] Перезапускаю nginx..."
sudo systemctl restart nginx