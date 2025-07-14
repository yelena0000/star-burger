# Сайт доставки еды Star Burger

[![Demo Version](https://img.shields.io/badge/демо--версия_сайта-%E2%86%92_Star_Burger-blue)](https://e-example.ru)

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом.

![Скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)

Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню и быстро оформить заказ без регистрации и SMS. Второй интерфейс предназначен для менеджера: здесь происходит обработка заказов. Менеджер подтверждает заказы, выбирает ближайший ресторан и передаёт заказ на исполнение. Третий интерфейс — админка, используемая программистами для разработки и менеджером для обновления меню.



## Подготовка сервера
Перед деплоем выполните следующие шаги:

1. **Установите зависимости**:
   - Docker и Docker Compose.
   - Nginx (настройте самостоятельно, см. ниже).
   - Certbot для HTTPS (настройте самостоятельно, см. ниже).

2. **Создайте необходимые папки**:
   - Создайте директории для статики и медиа на сервере:
     ```sh
     sudo mkdir -p /var/www/frontend
     sudo mkdir -p /var/www/media
     sudo chmod -R 755 /var/www/frontend /var/www/media
     ```

3. **Настройте Nginx:**
   - Установите Nginx: `sudo apt install nginx`.
   - Создайте конфигурационный файл (например, `/etc/nginx/sites-available/star-burger`):

```nginx
server {
    server_name your-domain.ru;

    location /static/ {
        alias /var/www/frontend/;
        access_log off;
        expires 30d;
    }

    location /media/ {
        alias /var/www/media/;
        access_log off;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

   - Активируйте конфиг: `sudo ln -s /etc/nginx/sites-available/star-burger /etc/nginx/sites-enabled/`.
   - Проверьте и перезапустите: `sudo nginx -t && sudo systemctl restart nginx`.

4. **Настройте HTTPS с Certbot:**
   - Установите Certbot: `sudo apt install certbot python3-certbot-nginx`.
   - Получите сертификат: `sudo certbot --nginx -d your-domain.com -m your-email@example.com --agree-tos --non-interactive`.
   - Настройте редирект HTTP → HTTPS в конфиге Nginx при необходимости.

## Как запустить dev-версию сайта
Для разработки сайта нужно запустить бэкенд и фронтенд одновременно. Используйте два терминала.

### Требования
- Python версии 3.6 или выше.
- Node.js версии не старше 17.6.0 (рекомендуется 16.16.0).
- Docker и Docker Compose.

### Шаги
1. Склонируйте репозиторий:
   ```sh
   git clone https://github.com/yelena0000/star-burger.git
   cd star-burger
   ```
2. Настройте переменные окружения:
   - Создайте файл `.env` в корне проекта:
     ```env
     SECRET_KEY=django-insecure-0if40nf4nf93n4
     YANDEX_GEOCODER_API_KEY=ваш_ключ_от_яндекса
     DEBUG=True
     ALLOWED_HOSTS=127.0.0.1,localhost
     DATABASE_URL=postgres://user:password@localhost:5432/dbname
     ```
   - Для локальной БД настройте PostgreSQL и обновите `DATABASE_URL`.
3. Запустите проект:
   ```sh
   docker-compose up --build
   ```
   - Бэкенд будет доступен на http://localhost:8000.
   - Фронтенд будет доступен на http://localhost:3000 (для отладки, но в dev-режиме используется бэкенд).
4. Проверка:
   - Откройте http://localhost:8000 в браузере.
   - Если статика не загружается, сбросьте кэш браузера (Ctrl-F5).

## Как запустить prod-версию сайта
Сайт развертывается на сервере с использованием Docker и Nginx. Следуйте инструкциям для деплоя.

### Требования
- Сервер с установленным Docker, Docker Compose, Nginx и Certbot.
- Доступ по SSH (например, root@your-server-ip).
- Домен, привязанный к IP сервера через A-запись.

### Настройка переменных окружения
Создайте файл `.env` в директории проекта на сервере (например, `/opt/star-burger/`):
```env
SECRET_KEY=django-insecure-0if40nf4nf93n4
YANDEX_GEOCODER_API_KEY=ваш_ключ_от_яндекса
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgres://user:password@db:5432/dbname
ROLLBAR_ACCESS_TOKEN=ваш_токен_rollbar
```

### Деплой на сервер
1. Подключитесь к серверу:
   ```sh
   ssh root@your-server-ip
   ```
2. Перейдите в директорию проекта:
   ```sh
   cd /opt/star-burger
   ```
3. Выполните деплой:
   ```sh
   ./deploy.sh
   ```
   - Скрипт обновит код, соберет контейнеры, применит миграции, скопирует бандлы и статику в `/var/www/frontend/`, и перезапустит Nginx.

4. Проверка:
   - Откройте http://your-domain.com в браузере.


### Описание деплоя
Процесс:
- Очищает временные папки (`/opt/star-burger/bundles`, `/var/www/frontend/`).
- Собирает фронтенд и бэкенд в контейнерах.
- Копирует бандлы из контейнера frontend и статику из backend в `/opt/star-burger/`.
- Копирует файлы в `/var/www/frontend/` для раздачи через Nginx.
- Применяет миграции и перезапускает сервисы.


## Мониторинг ошибок
Интеграция с Rollbar позволяет:
- Отслеживать ошибки в реальном времени.
- Просматривать историю деплоев.
- Связывать ошибки с версиями кода.

Настройте `ROLLBAR_ACCESS_TOKEN` в `.env` для активации.

## Цели проекта
Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте Devman. За основу взят код проекта FoodCart.

## Важно для деплоя
- После каждой сборки и команды `collectstatic` статика Django (включая админку) копируется в `/var/www/frontend/`, чтобы nginx мог корректно раздавать все статические файлы.
- Убедитесь, что папки `/var/www/frontend` и `/var/www/media` существуют на сервере и доступны для записи пользователю, под которым выполняется деплой.

## Как работает деплой
1. Очищаются временные папки (`/opt/star-burger/bundles`, `/var/www/frontend/`).
2. Собираются и запускаются контейнеры через `docker-compose.prod.yaml`.
3. Копируются бандлы фронта из контейнера frontend в `/opt/star-burger/bundles`, затем в `/var/www/frontend/`.
4. Применяются миграции и собирается статика Django (`collectstatic`).
5. Вся статика Django копируется из контейнера backend в `/var/www/frontend/` (см. скрипт `deploy.sh`).
6. Перезапускается nginx.

## Пример ручного копирования статики Django (если нужно)
```sh
# После collectstatic
sudo docker cp $(docker-compose -f docker-compose.prod.yaml ps -q backend):/app/staticfiles/. /var/www/frontend/
```

## Требования к папкам
Перед деплоем убедитесь, что папки для статики и media созданы:
```sh
sudo mkdir -p /var/www/frontend
sudo mkdir -p /var/www/media
sudo chmod -R 755 /var/www/frontend /var/www/media
```
