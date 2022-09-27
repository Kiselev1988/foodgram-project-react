![example workflow](https://github.com/Kiselev1988/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Foodgram


# Описание проекта

Сервис, в котором пользователи могут публиковать рецепты блюд, подписываться на других пользователей, добавлять рецепты в Избранное, скачивать список ингедиентов рецептов .


## Запуск проекта

Клонировать репозиторий и перейти в него:
```
git clone https://github.com/Kiselev1988/foodgram-project-react.git
```

Создать и активировать виртуальное окружение, обновить pip и установить зависимости:
```
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```
## Для работы с локальныйм сервером:

* Создание базы данных и администратора:
```
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
* Запуск сервера:

```
cd backend
python manage.py runserver
``` 

* Запуск фронтенда:

```
Из терминала выполнить команды:
cd infra
docker-compose up --build
```

## Для работы с удаленным сервером:
* Выполните вход на свой удаленный сервер через терминал
```
ssh <username>@<host>
```

* Установите docker на сервер:
```
sudo apt install docker.io 
```
* Установите docker-compose на сервер:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
* Локально отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP
* Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер:
```
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
* Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя>
    SECRET_KEY=<секретный ключ проекта django>
    USER=<username для подключения к серверу>
    HOST=<IP сервера>
    PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>
    TELEGRAM_TO=<ID чата, в который придет сообщение>
    TELEGRAM_TOKEN=<токен вашего бота>
    ```
   
    - Создать суперпользователя Django:
    ```
    sudo docker-compose exec backend python manage.py createsuperuser
    ```
    - Проект будет доступен по вашему IP


- Проект запущен и доступен по http://51.250.25.202/

- Админ панель http://51.250.25.202/admin/

- Админ логин: admin

- Админ пароль: admin
