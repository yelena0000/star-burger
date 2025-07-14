#!/bin/bash
cd /opt/star-burger
git pull

echo "[deploy] Очищаю временные папки..."
sudo rm -rf /var/www/frontend/*
sudo mkdir -p /var/www/frontend

echo "[deploy] Запускаю сборку контейнеров..."
docker-compose -f docker-compose.prod.yaml down
docker-compose -f docker-compose.prod.yaml up --build -d

echo "[deploy] Жду завершения сборки фронтенда..."
sleep 5

echo "[deploy] Применяю миграции и собираю статику..."
docker-compose -f docker-compose.prod.yaml exec backend python manage.py migrate
docker-compose -f docker-compose.prod.yaml exec backend python manage.py collectstatic --noinput

echo "[deploy] Перезапускаю nginx..."
sudo systemctl restart nginx