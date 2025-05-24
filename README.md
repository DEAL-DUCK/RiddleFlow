# RiddleFlow

## Описание

RiddleFlow — это платформа для организации и проведения хакатонов и контестов. Она включает в себя систему проверки решений и ролевую модель (участник/создатель). Платформа позволяет пользователям регистрироваться, участвовать в хакатонах, создавать задания и отправлять решения.

## Технологический стек

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic
- **База данных**: PostgreSQL
- **Кеширование**: Redis
- **Фоновые задачи**: Celery
- **Контейнеризация**: Docker

## Установка и запуск

### Предварительные требования

- Установите [Docker](https://www.docker.com/get-started) и [Docker Compose](https://docs.docker.com/compose/install/).

### Клонирование репозитория

```bash
git clone https://github.com/yourusername/RiddleFlow.git
cd RiddleFlow
```

Создайте виртуальное окружение и выполните миграции

```bash
cd services/backend/src
pip install -r requirements.txt
alembic upgrade head
```

### Запуск приложения

1. Соберите и запустите контейнеры:

```bash
docker-compose up -d --build
```

2. После успешного запуска, приложение будет доступно по адресу: `http://localhost:5000`.

### Доступ к Flower

Для мониторинга фоновых задач Celery, вы можете получить доступ к Flower по адресу: `http://localhost:5555`.

### Миграции базы данных

При первом запуске приложения, необходимо выполнить миграции базы данных:

```bash
docker-compose exec backend alembic upgrade head
```

### Остановка приложения

Чтобы остановить приложение, выполните:

```bash
docker-compose down
```

## Использование

- Зарегистрируйтесь как участник или создатель.
- Создавайте хакатоны и задания.
- Участвуйте в хакатонах, отправляя свои решения.

## Лицензия

Этот проект лицензирован под лицензией GNU General Public License v3.0. Подробности можно найти в файле LICENSE.


### Список использованных материалов и референсов 

При разработке проекта на **FastAPI** мы опирались на официальную документацию, статьи и обучающие материалы, чтобы обеспечить корректную реализацию ключевых компонентов системы.  

#### **Официальная документация**  
1. **FastAPI**  
   - [Документация FastAPI](https://fastapi.tiangolo.com/)  
   - Основной источник информации по построению API, работе с зависимостями (Dependency Injection), валидации данных через **Pydantic** и автоматической генерации OpenAPI-документации.  

2. **Celery**  
   - [Документация Celery](https://docs.celeryq.dev/)  
   - Использовалась для настройки фоновых задач. Особое внимание уделялось интеграции с **FastAPI** и мониторингу через **Flower**.  

3. **SQLAlchemy**  
   - [Документация SQLAlchemy](https://www.sqlalchemy.org/)  
   - Применялась для работы с реляционными базами данных в сочетании с **FastAPI** (через `SQLAlchemy ORM` и `asyncpg` для асинхронных запросов).  

4. **Redis**  
   - [Документация Redis](https://redis.io/documentation)  
   - Использовался как брокер сообщений для **Celery**, а также для кэширования часто запрашиваемых данных.  

#### **Дополнительные материалы**  
1. **Статья "Developing a Single-Page App with FastAPI and Vue.js"** (testdriven.io)  
   - [Ссылка](https://testdriven.io/blog/developing-a-single-page-app-with-fastapi-and-vuejs/#objectives)  
   - Помогла в настройке взаимодействия бэкенда (**FastAPI**) с фронтендом (**Vue.js**), включая CORS и асинхронные HTTP-запросы.  

2. **Обучающий плейлист по FastAPI** (YouTube)  
   - [Ссылка](https://www.youtube.com/watch?v=z4pbneT6SLw&list=PLYnH8mpFQ4akzzS1D9IHkMuXacb-bD4Cl)  
   - Разбор архитектурных решений, работы с **Pydantic**, **SQLAlchemy** и построения REST API.  

3. **Статья "Celery + Flower: асинхронные задачи в Python"** (Habr)  
   - [Ссылка](https://habr.com/ru/articles/733452/)  
   - Практическое руководство по настройке **Celery** и визуализации задач через **Flower**.