# Описание:
## Курс 8. Итоговое задание


## Задание
### Контейнеризируйте проект — создайте отдельные контейнеры: 
- для Django,
- PostgreSQL,
- Redis,
- Celery,
- Nginx,
- других сервисов, если они есть в проекте.
### Настройте запуск всех сервисов проекта через Docker Compose.
### Добавьте в репозиторий GitHub конфигурацию GitHub Actions, которая будет:
- запускать тесты и линтинг кода,
- проверять возможность сборки Docker-образов,
- при успешных проверках автоматически деплоить проект на сервер.
### Настройте удаленный сервер:
- убедитесь, что сервер готов к работе с Docker и Docker Compose.
- настройте SSH-доступ к серверу для деплоя через GitHub Actions.
### Подготовьте README.md:
- Опишите шаги настройки и запуска проекта локально.
- Добавьте инструкции по настройке CI/CD и деплоя на сервер.
### Убедитесь, что проект может быть запущен одной командой локально и автоматически разворачивается на удаленном сервере через GitHub Actions.

## Инструкция по настройке удалённого сервера и деплоя Django-приложения
В этом руководстве подробно описан процесс настройки удалённого сервера и автоматического деплоя Django-приложения с использованием Docker, Docker Compose, GitHub Actions и Nginx. Проект использует Celery, Redis, PostgreSQL, Telegram-бота и Gunicorn.

### 1. Настройка удалённого сервера (Ubuntu 20.04/22.04)
- Подключитесь к серверу по SSH
```
ssh username@ваш_сервер_ip
```
- Обновление системы
```
sudo apt update && sudo apt upgrade -y
```
- Установка Python и pip
```
sudo apt install python3 python3-pip python3-venv -y
```
- Установка Django и Gunicorn
```
pip3 install django gunicorn
```
Рекомендуется использовать виртуальное окружение в проекте. На сервере оно будет создаваться автоматически через GitHub Actions.

- Установка и настройка Nginx
```
sudo apt install nginx -y
```
- Запустите и включите автозагрузку
```
sudo systemctl start nginx
sudo systemctl enable nginx
```
- Настройка брандмауэра (UFW)

Разрешите только нужные порты
```
sudo ufw allow 'Nginx Full'    # порты 80 и 443
sudo ufw allow 'OpenSSH'       # порт 22
```
- Включите брандмауэр
```
sudo ufw enable
```
ВАЖНО: Убедитесь, что вы уже настроили SSH-ключи, иначе можете потерять доступ.

- Перезагрузите SSH
```
sudo systemctl restart ssh
```

### 2. Настройка CI/CD через GitHub Actions

- Создайте секреты в репозитории GitHub:
- Перейдите в Settings → Secrets and variables → Actions и добавьте:
- Создайте секреты:
```
SECRET_KEY	Ваш SECRET_KEY
DATABASE_NAME	course_5
DATABASE_USER	postgres
DATABASE_PASSWORD	Пароль от БД
DATABASE_HOST	localhost (в CI используется локальный контейнер)
DATABASE_PORT	5432
CELERY_BROKER_URL	redis://localhost:6379/0
CELERY_RESULT_BACKEND	redis://localhost:6379/0
TELEGRAM_TOKEN	Токен от @BotFather
DOCKER_HUB_USERNAME	Ваш логин в Docker Hub
DOCKER_HUB_ACCESS_TOKEN	
SSH_USER	root или ваш пользователь
SSH_KEY	Приватный SSH-ключ (с новой строки)
SERVER_IP	IP-адрес вашего сервера
```

- Добавьте публичный ключ на сервер:
```
sudo nano /root/.ssh/authorized_keys
```
3. Деплой через GitHub Actions

При пуше в ветку main произойдёт:
```
Линтинг (flake8)
Тесты с PostgreSQL
Сборка Docker-образа и пуш в Docker Hub
Деплой на сервер через SSH
```
## Адрес сервера с развернутым приложением:
```
217.28.226.26
```

## Документация:
Настоящий файл [README.md](README.md).

## Лицензия:
Проект распространяется под [лицензией MIT](LICENSE). 