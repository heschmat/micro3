Goal:
A single source of truth (Postgres) that tracks every video through the pipeline.

```sh
#

uv add sqlalchemy alembic psycopg2-binary

## initialize alembic
uv run alembic init alembic

```

Edit `alembic.ini`
```md
# sqlalchemy.url = driver://user:pass@localhost/dbname
sqlalchemy.url = postgresql://postgres:pgpass123@localhost:5432/videos
```


Edit `alembic/env.py`
```py
from app.db import Base
from app import models

target_metadata = Base.metadata
```

Create the first migration & apply:
```sh
uv run alembic revision --autogenerate -m "create videos table"

uv run alembic upgrade head
```



NOTE:

```py
# NOW we have:
db.commit()
publish_message()

# If publish fails → DB says uploaded but no job exists ❌
# =>
try:
    upload_file(file.file, file_path)

    video = Video(...)
    db.add(video)
    db.commit()

    publish_message(message)

except Exception:
    db.rollback()
    raise
```



# auth

```sh
uv add pyjwt "passlib[bcrypt]"
uv add argon2-cffi

#uv run alembic revision -m "add users and video ownership"
uv run alembic revision --autogenerate -m "add users and video ownership"

uv run alembic upgrade head

docker compose exec upload-service uv run alembic upgrade head
```

test
```sh
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'


curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'


ACC_TOKEN='ey...'
curl http://localhost:8000/auth/me \
  --cookie "access_token=$ACC_TOKEN"


# or: login & save cookie
curl -i -c cookies.txt -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

curl -b cookies.txt http://localhost:8000/auth/me
```


## alembic

```sh

grep -R "a1dd1b4ea66c" alembic/
# grep: alembic/versions/__pycache__/a1dd1b4ea66c_add_users_and_video_ownership.cpython-312.pyc: binary file matches


rm -rf alembic/versions/__pycache__

uv run alembic revision --autogenerate -m "add users and video ownership"

uv run alembic current


# ---
uv run python - <<'PY'
import os
from sqlalchemy import create_engine, text
engine = create_engine(os.environ["DATABASE_URL"])
with engine.connect() as conn:
    print(conn.execute(text("select version_num from alembic_version")).fetchall())
PY
# ---

uv run alembic stamp 030a90e4080c



# ---
uv run python - <<'PY'
import os
from sqlalchemy import create_engine, text

engine = create_engine(os.environ["DATABASE_URL"])

with engine.begin() as conn:
    conn.execute(text("UPDATE alembic_version SET version_num = :v"), {"v": "030a90e4080c"})
    rows = conn.execute(text("SELECT version_num FROM alembic_version")).fetchall()
    print(rows)
PY
# ---

uv run alembic current # 030a90e4080c (head)

uv run alembic revision --autogenerate -m "add users and video ownership"

uv run alembic upgrade head
# docker compose exec upload-service uv run alembic upgrade head
```

