# Шаг 5. Docstrings — проверка

1. VS Code → открыть `src/api/contacts.py` → навести курсор на `ContactService` и на `get_current_user`
2. Вывести docstring в консоль:

```bash
docker compose exec app python -c "from src.repository.contacts import ContactRepository; help(ContactRepository.get_upcoming_birthdays)"
```

3. Swagger http://localhost:8000/docs → раскрыть `POST /api/auth/reset_password` и `PATCH /api/users/avatar`
4. Swagger → любой контакт-маршрут → Try it out → Execute (всё работает как раньше)
