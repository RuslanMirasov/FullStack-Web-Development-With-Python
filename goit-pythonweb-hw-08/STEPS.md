# Шаг 1. Окружение и Docker

### 1.1. Виртуальное окружение и пакеты

```bash
cd goit-pythonweb-hw-08
python -m venv venv
source venv/Scripts/activate
pip install "fastapi[standard]" "sqlalchemy[asyncio]" asyncpg alembic python-dotenv faker
pip freeze > requirements.txt
```

VS Code: **Ctrl+Shift+P → Python: Select Interpreter → ./venv**

### 1.2. Структура папок

```bash
mkdir -p src/api src/services src/repository src/database src/conf
```

### 1.3. `.env.example`

```
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=
```

### 1.4. `.env`

```
POSTGRES_DB=hw08
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123qweQ
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 1.5. `.dockerignore`

```
venv/
__pycache__/
*.pyc
.git/
postgres-data/
.env
```

### 1.6. `Dockerfile`

```dockerfile
FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.7. `docker-compose.yaml`

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - '5432:5432'
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}']
      interval: 2s
      timeout: 3s
      retries: 10
      start_period: 60s

  app:
    build: .
    env_file: .env
    environment:
      POSTGRES_HOST: db
    ports:
      - '8000:8000'
    depends_on:
      db:
        condition: service_healthy
```

### 1.8. `docker-compose.override.yaml`

```yaml
services:
  app:
    entrypoint: ['uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000', '--reload', '--reload-dir', 'src']
    environment:
      WATCHFILES_FORCE_POLLING: 'true'
    volumes:
      - .:/app
```

### 1.9. `main.py` (временный)

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI!"}
```

### 1.10. Запуск

```bash
docker compose up -d --build
```

Открыть http://localhost:8000/docs

# Шаг 2. Конфиг и подключение к БД

### 2.1. `src/conf/config.py`

```python
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")

    DB_URL = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )


config = Config
```

### 2.2. `src/database/db.py`

```python
import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import config


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session
```

### 2.3. `src/api/utils.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
```

### 2.4. `main.py`

```python
from fastapi import FastAPI

from src.api import utils

app = FastAPI()

app.include_router(utils.router, prefix="/api")
```

### 2.5. Перезапуск

```bash
docker compose restart app
```

Открыть http://localhost:8000/docs → `GET /api/healthchecker` → Execute
