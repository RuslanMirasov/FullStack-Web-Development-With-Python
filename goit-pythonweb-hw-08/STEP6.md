# Шаг 6. Поиск и дни рождения

### 6.1. `src/repository/contacts.py`

Заменить импорты:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
```

на:

```python
from datetime import date, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
```

---

Заменить метод `get_contacts` на:

```python
    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> list[Contact]:
        stmt = select(Contact)
        if first_name:
            stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            stmt = stmt.where(Contact.email.ilike(f"%{email}%"))
        stmt = stmt.offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_upcoming_birthdays(self, days: int) -> list[Contact]:
        today = date.today()
        end_date = today + timedelta(days=days)
        birthday_md = func.to_char(Contact.birthday, "MM-DD")
        start_md = today.strftime("%m-%d")
        end_md = end_date.strftime("%m-%d")

        if start_md <= end_md:
            condition = birthday_md.between(start_md, end_md)
        else:
            condition = or_(birthday_md >= start_md, birthday_md <= end_md)

        stmt = select(Contact).where(condition).order_by(birthday_md)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
```

### 6.2. `src/services/contacts.py`

Заменить метод `get_contacts` на:

```python
    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ):
        return await self.repository.get_contacts(
            skip, limit, first_name, last_name, email
        )

    async def get_upcoming_birthdays(self, days: int):
        return await self.repository.get_upcoming_birthdays(days)
```

### 6.3. `src/api/contacts.py`

Заменить функцию `read_contacts` на:

```python
@router.get("/", response_model=list[ContactResponse])
async def read_contacts(
    first_name: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await ContactService(db).get_contacts(
        skip, limit, first_name, last_name, email
    )


@router.get("/birthdays", response_model=list[ContactResponse])
async def read_upcoming_birthdays(
    days: int = Query(default=7, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    return await ContactService(db).get_upcoming_birthdays(days)
```

### 6.4. Проверка в Swagger http://localhost:8000/docs

1. `POST /api/contacts/`:

```json
{
  "first_name": "Olena",
  "last_name": "Shevchenko",
  "email": "olena@example.com",
  "phone": "+380501112233",
  "birthday": "1995-10-02"
}
```

2. `POST /api/contacts/`:

```json
{
  "first_name": "Oleh",
  "last_name": "Kovalenko",
  "email": "oleh@test.com",
  "phone": "+380631234567",
  "birthday": "1988-12-25"
}
```

3. `GET /api/contacts/` → `first_name` = `ole`
4. `GET /api/contacts/` → `last_name` = `shev`
5. `GET /api/contacts/` → `email` = `test.com`
6. `GET /api/contacts/birthdays`
7. `GET /api/contacts/birthdays` → `days` = `90`
