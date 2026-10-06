# Contacts API (ДЗ #11)

REST API для зберігання та управління контактами на FastAPI + SQLAlchemy 2 + PostgreSQL + Pydantic.

## Запуск

```bash
# 1. PostgreSQL у Docker (порт задається в .env, за замовчуванням 5433)
cp .env.example .env        # і вкажіть свій пароль
docker compose up -d

# 2. Залежності
python -m venv .venv
.venv\Scripts\activate      # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt

# 3. Міграції (створення таблиць)
alembic upgrade head

# 4. Сервер
uvicorn main:app --reload
```

Документація: http://127.0.0.1:8000/docs (Swagger) та http://127.0.0.1:8000/redoc

## Ендпоінти

| Метод  | Шлях                          | Опис |
|--------|-------------------------------|------|
| POST   | `/api/contacts/`              | Створити контакт |
| GET    | `/api/contacts/`              | Список контактів; пошук `?first_name=&last_name=&email=` (частковий, без урахування регістру), пагінація `?skip=&limit=` |
| GET    | `/api/contacts/{id}`          | Отримати контакт за id |
| PUT    | `/api/contacts/{id}`          | Оновити контакт (лише передані поля) |
| DELETE | `/api/contacts/{id}`          | Видалити контакт |
| GET    | `/api/contacts/birthdays`     | Дні народження на найближчі 7 днів (`?days=N` для іншого періоду) |
| GET    | `/api/healthchecker`          | Перевірка з'єднання з БД |

## Структура

```
main.py                    # застосунок FastAPI
src/conf/config.py         # налаштування з .env (pydantic-settings)
src/database/db.py         # engine, сесії, залежність get_db
src/database/models.py     # ORM-модель Contact
src/schemas.py             # Pydantic-схеми та валідація
src/repository/contacts.py # робота з БД
src/routes/contacts.py     # маршрути API
migrations/                # міграції Alembic (URL БД береться з .env)
```

## Міграції

```bash
alembic revision --autogenerate -m "опис змін"   # після зміни моделей
alembic upgrade head                            # застосувати
alembic downgrade -1                            # відкотити останню
```
