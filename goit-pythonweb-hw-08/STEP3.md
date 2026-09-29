# Шаг 3. Модель Contact и миграции

### 3.1. `src/database/models.py`

```python
from datetime import date, datetime

from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    birthday: Mapped[date] = mapped_column(nullable=False)
    additional_data: Mapped[str | None] = mapped_column(String(250))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )
```

### 3.2. Инициализация Alembic

```bash
cd goit-pythonweb-hw-08
source venv/Scripts/activate
alembic init -t async migrations
```

### 3.3. `migrations/env.py`

Заменить:

```python
from alembic import context
```

на:

```python
from alembic import context

from src.conf.config import config as app_config
from src.database.models import Base
```

---

Заменить:

```python
config = context.config
```

на:

```python
config = context.config
config.set_main_option("sqlalchemy.url", app_config.DB_URL)
```

---

Заменить:

```python
target_metadata = None
```

на:

```python
target_metadata = Base.metadata
```

### 3.4. Создать и применить миграцию

```bash
docker compose exec app alembic revision --autogenerate -m 'Init'
docker compose exec app alembic upgrade head
```

### 3.5. Проверить таблицу

```bash
docker compose exec db sh -c 'psql -U $POSTGRES_USER -d $POSTGRES_DB -c "\d contacts"'
```
