# Тема 8. Домашня робота

## Запуск

Створіть файл `.env`, заповнивши його за прикладом `.env.example` своїми значеннями.

```bash
POSTGRES_DB=hw08
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123qweQ
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Команди:

```bash
docker compose up -d --build                  # піднімає Postgres + контейнер застосунку
docker compose exec app alembic upgrade head  # застосувати міграції, створити таблицю contacts
```

Swagger документація: http://localhost:8000/docs

## Ендпоінти

| Метод  | URL                          | Опис                                                        |
| ------ | ---------------------------- | ----------------------------------------------------------- |
| GET    | `/api/healthchecker`         | Перевірка підключення до бази даних                         |
| GET    | `/api/contacts/`             | Список контактів, пошук: `first_name`, `last_name`, `email` |
| GET    | `/api/contacts/birthdays`    | Дні народження на найближчі 7 днів (`days`)                 |
| GET    | `/api/contacts/{contact_id}` | Контакт за ідентифікатором                                  |
| POST   | `/api/contacts/`             | Створити контакт                                            |
| PUT    | `/api/contacts/{contact_id}` | Оновити контакт                                             |
| DELETE | `/api/contacts/{contact_id}` | Видалити контакт                                            |
