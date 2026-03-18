
# 
```sh
cd infra
docker compose up -d

```

Verify

1) RabbitMQ UI: http://localhost:15672 
login: guest / guest


2) MinIO console: http://localhost:9001 
login: minio / minio123

3) 👉 Create 2 buckets manually:
- videos
- audios


# upload-service 

Make sure `uv` is installed

```sh
curl -Ls https://astral.sh/uv/install.sh | sh

```

Then restart your terminal or run: `source ~/.zshrc`


Verify

```sh
uv --version
```

```sh
cd upload-service

uv init
uv venv
source .venv/bin/activate

uv add fastapi uvicorn boto3 pika python-multipart python-dotenv

```


Run & test
```sh
uv run uvicorn app.main:app --reload --port 8000


curl -F "file=@test.mp4" http://localhost:8000/upload
```

# converter

```sh
sudo apt update
sudo apt install ffmpeg -y

# check
ffmpeg -version
```

If it works, tag
```sh
git add .
git commit -m "feat: end-to-end pipeline working (upload -> convert -> store)"
git tag v0.2-end-to-end-pipeline
git push origin v0.2-end-to-end-pipeline
```