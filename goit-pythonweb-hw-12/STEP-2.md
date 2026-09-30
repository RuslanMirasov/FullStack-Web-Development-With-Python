# Шаг 2. Ролі user / admin

### 2.5. Удалить старые миграции и базу

```bash
docker compose down
rm -rf postgres-data
rm migrations/versions/*.py
docker compose up -d
```

### 2.6. Создать одну миграцию

```bash
docker compose exec app alembic revision --autogenerate -m 'Init'
```

### 2.7. Поправить `downgrade()` в созданном файле `migrations/versions/..._init.py`

В конце `downgrade()`, после последней строки `op.drop_table(...)`, добавить:

```python
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
```

### 2.8. Применить миграцию

```bash
docker compose exec app alembic upgrade head
docker compose exec app alembic current
```

### 2.9. Проверка в Swagger http://localhost:8000/docs

1. `POST /api/auth/register`:

```json
{
  "username": "ruslan",
  "email": "mirasovdev@gmail.com",
  "password": "secret123"
}
```

2. Подтвердить почту по ссылке из письма
3. **Authorize** как `ruslan` → `GET /api/users/me`
4. `PATCH /api/users/avatar` → выбрать картинку → Execute
5. Сделать `ruslan` админом:

```bash
docker compose exec db sh -c 'psql -U $POSTGRES_USER -d $POSTGRES_DB -c "UPDATE users SET role = '"'"'ADMIN'"'"' WHERE username = '"'"'ruslan'"'"'"'
```

6. `GET /api/users/me`
7. `PATCH /api/users/avatar` → выбрать картинку → Execute
