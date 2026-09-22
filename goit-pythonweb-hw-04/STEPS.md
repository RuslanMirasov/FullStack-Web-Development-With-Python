# Шаг 1 окружение и Docker-скелет:

### 1. Создать и активировать виртуальное окружение:

```
python -m venv venv
source venv/Scripts/activate
```

### 2. Установить и зафиксировать зависимости в файл requirements.txt

```
pip install jinja2
pip freeze > requirements.txt
```

### 3. Указать VS Code, какой Python использовать: **Ctrl+Shift+P → Python: Select Interpreter → выбрать вариант из ./venv.**

### 4. Создать Dockerfile (без расширения):

```Python
FROM python:3.10

ENV APP_HOME /app
WORKDIR $APP_HOME

COPY . .

RUN pip install -r requirements.txt

EXPOSE 3000

ENTRYPOINT ["python", "main.py"]
```

- FROM python:3.10 — берём готовый образ с уже установленным Python 3.10 как основу
- WORKDIR $APP_HOME — все следующие команды выполняются внутри папки /app в контейнере
- COPY . . — копируем всё содержимое проекта внутрь образа
- RUN pip install -r requirements.txt — при сборке образа ставим зависимости внутри контейнера Docker
- EXPOSE 3000 — сообщаем Docker, какой порт слушает приложение
- ENTRYPOINT [...] — команда, которая запускается при старте контейнера

### 7. Создать .dockerignore файл

```
venv/
__pycache__/
*.pyc
.git/
```

### 8. Создать docker-compose.yaml

```Python
version: "3"
services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./storage:/app/storage
```

- **build:** . — собрать образ из Dockerfile, который лежит рядом (в этой же папке)
- **ports:** "3000:3000" — пробросить порт 3000 хоста на порт 3000 внутри контейнера
- **volumes:** ./storage:/app/storage — папка storage на диске монтируется внутрь контейнера, поэтому data.json сохранится даже
  после удаления контейнера

### 9. Создаём файл main.py

#### Для HTTP Server (без Framework)

```Python
from http.server import HTTPServer, BaseHTTPRequestHandler


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'It works! Server is running on port 3000.')


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('0.0.0.0', 3000)
    http = server_class(server_address, handler_class)
    print('Starting server on port 3000...')
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
```

#### Для FastAPI Framework

Установка (в venv, только для этого проекта):

```
pip install fastapi uvicorn
pip freeze > requirements.txt
```

```Python
from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get('/')
def index():
    return {'message': 'It works! Server is running on port 3000.'}


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=3000, reload=True)
```

- `FastAPI()` — создаёт приложение, аналог `HttpHandler` из версии без фреймворка, только маршруты вешаются декораторами, а не
  методами `do_GET`/`do_POST`
- `@app.get('/')` — регистрирует маршрут `GET /`; для `POST` было бы `@app.post('/...')`
- `uvicorn` — ASGI-сервер, который реально запускает и слушает порт (сам FastAPI — только про маршруты и логику, без сервера)
- `uvicorn.run('main:app', ...)` — первая часть строки `'main:app'` означает "переменная `app` в файле `main.py`"; если
  переименуешь файл, поменяй и эту строку
- `reload=True` — сервер сам перезапускается при изменении кода (удобно для разработки, для продакшн-контейнера обычно убирают)
- в `Dockerfile` для FastAPI-проекта `ENTRYPOINT` тот же — `["python", "main.py"]`, EXPOSE меняешь под нужный порт

### Команды для запуска

Одинаковые для http.server и FastAPI-версий — framework внутри `main.py`.

**Локально, через venv (без Docker):**

```bash
source venv/Scripts/activate
python main.py
```

**Только для FastAPI — альтернативный способ, без `python main.py`, напрямую через uvicorn:**

```bash
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

**Через Docker (одна команда, без compose):**

```bash
docker build -t project-name .
docker run -p 3000:3000 -v "$(pwd)/storage:/app/storage" project-name
```

**Через Docker Compose (если есть docker-compose.yaml):**

```bash
docker compose up --build
```

`--build` нужен не всегда:

- менял `Dockerfile`, `requirements.txt` или код проекта → `docker compose up --build` (пересобрать образ)
- ничего не менял, просто хочешь снова поднять то, что уже собрано → достаточно `docker compose up` без флага

Без `--build` Compose пересоберёт образ, только если его ещё вообще нет — если он есть, но устарел (код поменялся), запустится
старая версия без предупреждения.

Остановить: `Ctrl+C`, затем, если запускал через compose — ещё `docker compose down` (удаляет контейнер и сеть, volume с данными
не трогает).
