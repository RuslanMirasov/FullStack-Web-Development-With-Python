# Шаг 5. CRUD: репозиторий, сервис, роутер

### 5.1. `src/repository/contacts.py`

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactModel


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int) -> list[Contact]:
        stmt = select(Contact).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def get_contact_by_email(self, email: str) -> Contact | None:
        stmt = select(Contact).filter_by(email=email)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True))
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactModel
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            for key, value in body.model_dump().items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact
```

### 5.2. `src/services/contacts.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactModel


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def get_contacts(self, skip: int, limit: int):
        return await self.repository.get_contacts(skip, limit)

    async def get_contact(self, contact_id: int):
        return await self.repository.get_contact_by_id(contact_id)

    async def get_contact_by_email(self, email: str):
        return await self.repository.get_contact_by_email(email)

    async def create_contact(self, body: ContactModel):
        return await self.repository.create_contact(body)

    async def update_contact(self, contact_id: int, body: ContactModel):
        return await self.repository.update_contact(contact_id, body)

    async def remove_contact(self, contact_id: int):
        return await self.repository.remove_contact(contact_id)
```

### 5.3. `src/api/contacts.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactModel, ContactResponse
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=list[ContactResponse])
async def read_contacts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await ContactService(db).get_contacts(skip, limit)


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await ContactService(db).get_contact(contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post(
    "/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED
)
async def create_contact(body: ContactModel, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    if await contact_service.get_contact_by_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with this email already exists",
        )
    return await contact_service.create_contact(body)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel, contact_id: int, db: AsyncSession = Depends(get_db)
):
    contact_service = ContactService(db)
    existing = await contact_service.get_contact_by_email(body.email)
    if existing and existing.id != contact_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with this email already exists",
        )
    contact = await contact_service.update_contact(contact_id, body)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await ContactService(db).remove_contact(contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
```

### 5.4. `main.py`

```python
from fastapi import FastAPI

from src.api import contacts, utils

app = FastAPI()

app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
```

### 5.5. Перезапуск

```bash
docker compose restart app
```

### 5.6. Проверка в Swagger http://localhost:8000/docs

1. `POST /api/contacts/`:

```json
{
  "first_name": "Ivan",
  "last_name": "Petrenko",
  "email": "ivan@example.com",
  "phone": "+380671234567",
  "birthday": "1990-05-17",
  "additional_data": "Friend from university"
}
```

2. `POST /api/contacts/` с тем же телом ещё раз
3. `GET /api/contacts/`
4. `GET /api/contacts/{contact_id}` с id из шага 1
5. `PUT /api/contacts/{contact_id}` с изменённым `phone`
6. `DELETE /api/contacts/{contact_id}`
7. `GET /api/contacts/{contact_id}` с тем же id
