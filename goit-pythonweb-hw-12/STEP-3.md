# Шаг 3. Кеширование текущего пользователя в Redis

### 3.1. `src/database/redis.py`

```python
import redis.asyncio as redis

from src.conf.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
)


async def get_redis():
    return redis_client
```

### 3.2. `src/services/auth.py`

Заменить:

```python
from datetime import UTC, datetime, timedelta
```

на:

```python
import json
from datetime import UTC, datetime, timedelta
```

---

Заменить:

```python
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
```

на:

```python
from passlib.context import CryptContext
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
```

---

Заменить:

```python
from src.database.models import User, UserRole
```

на:

```python
from src.database.models import User, UserRole
from src.database.redis import get_redis
```

---

Заменить всю функцию `get_current_user` на:

```python
def user_cache_key(username: str) -> str:
    return f"user:{username}"


def user_to_cache(user: User) -> str:
    return json.dumps(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar,
            "confirmed": user.confirmed,
            "role": user.role.value,
        }
    )


def user_from_cache(data: str) -> User:
    user_data = json.loads(data)
    user_data["role"] = UserRole(user_data["role"])
    return User(**user_data)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(get_redis),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    cached_user = await cache.get(user_cache_key(username))
    if cached_user:
        return user_from_cache(cached_user)

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    await cache.set(
        user_cache_key(username),
        user_to_cache(user),
        ex=settings.REDIS_TTL_SECONDS,
    )
    return user
```

### 3.3. `src/api/users.py`

Заменить:

```python
from fastapi import APIRouter, Depends, File, Request, UploadFile
from slowapi import Limiter
```

на:

```python
from fastapi import APIRouter, Depends, File, Request, UploadFile
from redis.asyncio import Redis
from slowapi import Limiter
```

---

Заменить:

```python
from src.database.db import get_db
```

на:

```python
from src.database.db import get_db
from src.database.redis import get_redis
```

---

Заменить:

```python
from src.services.auth import get_current_admin_user, get_current_user
```

на:

```python
from src.services.auth import (
    get_current_admin_user,
    get_current_user,
    user_cache_key,
)
```

---

Заменить всю функцию `update_avatar_user` на:

```python
@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(get_redis),
):
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)
    await cache.delete(user_cache_key(user.username))
    return user
```

### 3.4. `src/repository/contacts.py`

Заменить:

```python
        stmt = select(Contact).filter_by(user=user)
```

на:

```python
        stmt = select(Contact).filter_by(user_id=user.id)
```

---

Заменить:

```python
            .filter_by(user=user)
```

на:

```python
            .filter_by(user_id=user.id)
```

---

Заменить:

```python
        stmt = select(Contact).filter_by(id=contact_id, user=user)
```

на:

```python
        stmt = select(Contact).filter_by(id=contact_id, user_id=user.id)
```

---

Заменить:

```python
        stmt = select(Contact).filter_by(email=email, user=user)
```

на:

```python
        stmt = select(Contact).filter_by(email=email, user_id=user.id)
```

---

Заменить:

```python
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
```

на:

```python
        contact = Contact(**body.model_dump(exclude_unset=True), user_id=user.id)
```

### 3.5. Проверка

1. Swagger http://localhost:8000/docs → **Authorize** как `ruslan` → `GET /api/users/me`
2. Посмотреть кеш:

```bash
docker compose exec redis redis-cli keys '*'
docker compose exec redis redis-cli get user:ruslan
docker compose exec redis redis-cli ttl user:ruslan
```

3. `POST /api/contacts/`:

```json
{
  "first_name": "Olena",
  "last_name": "Shevchenko",
  "email": "olena@example.com",
  "phone": "+38 (050) 111-22-33",
  "birthday": "1995-10-02"
}
```

4. `GET /api/contacts/`
5. `PATCH /api/users/avatar` → выбрать картинку → Execute
6. Проверить, что кеш сброшен:

```bash
docker compose exec redis redis-cli get user:ruslan
```

7. `GET /api/users/me` → в `avatar` новая ссылка
