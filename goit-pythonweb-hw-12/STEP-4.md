# Шаг 4. Сброс пароля — проверка одноразового токена

### Проверка в Swagger http://localhost:8000/docs

1. `POST /api/auth/request_password_reset`:

```json
{
  "email": "mirasovdev@gmail.com"
}
```

2. `POST /api/auth/reset_password` с новым токеном из письма:

```json
{
  "token": "<новый токен из письма>",
  "password": "secret123"
}
```

3. `POST /api/auth/reset_password` с тем же токеном ещё раз
4. `POST /api/auth/login` → `ruslan` / `secret123`
