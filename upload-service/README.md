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
