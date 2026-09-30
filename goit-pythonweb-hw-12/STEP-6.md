# Шаг 6. Тесты и покрытие — проверка

### 6.1. Запустить все тесты

```bash
source venv/Scripts/activate
pytest -v
```

### 6.2. Покрытие в консоли

```bash
pytest --cov=src --cov-report=term-missing
```

### 6.3. Покрытие в HTML

```bash
pytest --cov=src --cov-report=html
```

Открыть `htmlcov/index.html` в браузере.

### 6.4. Исправленная сортировка дней рождения в Swagger

1. `POST /api/contacts/` — контакт с днём рождения в январе:

```json
{
  "first_name": "Oleh",
  "last_name": "Kovalenko",
  "email": "oleh@example.com",
  "phone": "+38 (063) 123-45-67",
  "birthday": "1988-01-05"
}
```

2. `POST /api/contacts/` — контакт с днём рождения в октябре:

```json
{
  "first_name": "Iryna",
  "last_name": "Bondar",
  "email": "iryna@example.com",
  "phone": "+38 (097) 765-43-21",
  "birthday": "1992-10-10"
}
```

3. `GET /api/contacts/birthdays` → `days` = `120`
