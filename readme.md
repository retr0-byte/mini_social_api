## Mini Social API


### Опис

**Mini Social API** — спрощений REST API для соціальної платформи.
Сервіс дозволяє користувачам реєструватися, автентифікуватися, створювати пости та взаємодіяти з ними через систему лайків.

Проєкт реалізовано як MVP з фокусом на:
- чисту архітектуру
- асинхронну роботу з БД
- коректну авторизацію
- конкурентні сценарії (likes)


### Стек

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0 (async)
- Alembic
- Pydantic v2
- JWT (access + refresh)
- Docker, docker-compose


### Як запускати
##### Підготовка .env
Створи файл .env в корені проєкту (поруч з docker-compose.yml) і заповни змінні(приклад у .env.example)

Для Docker DB_HOST має бути db.

##### Запуск через Docker Compose

З кореня проєкту:

`docker compose up --build -d`


Перевірити логи:

`docker compose logs -f api`
`docker compose logs -f db`


API буде доступне за адресою:

http://localhost:8000

Swagger: http://localhost:8000/docs

##### Міграції

Виконати всередині контейнера api:

`docker compose exec api alembic upgrade head`

### API ендпоінти

#### Auth router:

- Post "/signup" — Реєстрація користувача
- Post "/signin" — Вхід (отримання access/refresh токенів і запис refresh у бд)
- Post "/refresh" — Оновлення access токена по refresh токену
- Post "/logout" — Вихід (Видалення токенів)

#### Post router:

- Get "/posts" — Список постів (усі або конкретного користувача)
- Get "/post/{post_id}" — Деталі конкретного поста
- Post "/post" — Створення нового поста
- Patch "/post/{post_id}" — Оновлення поста (часткове)
- Delete "/post/{post_id}" — Видалення поста

#### Like router:

- Post "/like/{post_id}" - Лайк
- Delete "/like/{post_id}" - Прибрати лайк

### Оцінка часу

Орієнтовний час розробки MVP:
- Налаштування проекту (Docker, Alembic, базова структура, налаштування) — 1 день
- Аутентифікація (hash паролю, JWT access/refresh, статус коди) — 1,5 дня
- CRUD публікацій (CRUD, пагінація, дії доступні автору, author + likes_count у відповіді) — 2 дні
- Лайки (ідемпотентність, паралельність) — 1.5 день
- Доопрацювання - 1 день

Всього: близько 7 робочіх днів