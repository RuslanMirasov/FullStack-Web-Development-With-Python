# Шаг 4. Pydantic-схемы

### 4.1. `src/schemas.py`

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, PastDate


class ContactModel(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=100)
    phone: str = Field(min_length=7, max_length=20, pattern=r"^\+?[\d\s\-()]+$")
    birthday: PastDate
    additional_data: str | None = Field(default=None, max_length=250)


class ContactResponse(ContactModel):
    id: int
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
```

### 4.2. Проверка: валидные данные

```bash
docker compose exec app python -c "from src.schemas import ContactModel; print(ContactModel(first_name='Ivan', last_name='Petrenko', email='ivan@example.com', phone='+380 (67) 123-45-67', birthday='1990-05-17'))"
```

### 4.3. Проверка: невалидные данные

```bash
docker compose exec app python -c "from src.schemas import ContactModel; ContactModel(first_name='', last_name='P', email='bad', phone='abc', birthday='2999-01-01')"
```
