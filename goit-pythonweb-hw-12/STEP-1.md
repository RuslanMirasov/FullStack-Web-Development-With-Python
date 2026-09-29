# Шаг 1. Окружение, зависимости, Redis, настройки тестов

### 1.1. Виртуальное окружение и пакеты

```bash
cd goit-pythonweb-hw-12
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
pip install redis pytest pytest-asyncio pytest-cov pytest-mock aiosqlite sphinx
pip freeze > requirements.txt
```

VS Code: **Ctrl+Shift+P → Python: Select Interpreter → ./venv**

### 1.2. `.env`

```bash
cp ../goit-pythonweb-hw-10/.env .env
```

Добавить в конец `.env`:

```

REDIS_HOST=localhost
REDIS_PORT=6379
```

### 1.3. `.env.example` — добавить в конец

```

REDIS_HOST=
REDIS_PORT=
```

### 1.4. `src/conf/config.py`

Заменить:

```python
    CLD_NAME: str
    CLD_API_KEY: str
    CLD_API_SECRET: str
```

на:

```python
    CLD_NAME: str
    CLD_API_KEY: str
    CLD_API_SECRET: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_TTL_SECONDS: int = 900
```

### 1.5. `docker-compose.yaml`

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

  redis:
    image: redis:7
    ports:
      - '6379:6379'
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']
      interval: 2s
      timeout: 3s
      retries: 10

  app:
    build: .
    env_file: .env
    environment:
      POSTGRES_HOST: db
      REDIS_HOST: redis
    ports:
      - '8000:8000'
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
```

### 1.6. `pyproject.toml`

```toml
[tool.pytest.ini_options]
pythonpath = "."
testpaths = ["tests"]
asyncio_default_fixture_loop_scope = "function"
filterwarnings = "ignore::DeprecationWarning"
```

### 1.7. Запуск

```bash
docker compose up -d --build
docker compose exec app alembic upgrade head
docker compose exec redis redis-cli ping
```

Открыть http://localhost:8000/docs → `GET /api/healthchecker` → Execute
