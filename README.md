# microservie demo

## initial setup 
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


## upload-service 

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

VIDEO_ID="47c7c5cb-ff45-4c62-815f-b98898039527"
curl http://localhost:8000/videos/$VIDEO_ID
```

## converter

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


## notification

```sh
uv run uvicorn app.main:app --reload --port 8100
```


```sh
# upload video
curl -F "file=@test.mp4" http://localhost:8000/upload
{"status":"success","video_id":"2b623bf8-eb92-4d33-b9c2-c7e9615da1b0"}

# ------------ upload service

2026-03-18 22:26:47,423 [INFO] [upload-service] Received upload: test.mp4
2026-03-18 22:26:47,423 [INFO] [upload-service] Generated video_id: 2b623bf8-eb92-4d33-b9c2-c7e9615da1b0
2026-03-18 22:26:47,423 [INFO] [upload-service] Uploading file to S3: 2b623bf8-eb92-4d33-b9c2-c7e9615da1b0.mp4
2026-03-18 22:26:47,557 [INFO] [upload-service] Upload successful: 2b623bf8-eb92-4d33-b9c2-c7e9615da1b0.mp4
2026-03-18 22:26:47,566 [INFO] [upload-service] Publishing message: {'video_id': '2b623bf8-eb92-4d33-b9c2-c7e9615da1b0', 'file_path': '2b623bf8-eb92-4d33-b9c2-c7e9615da1b0.mp4', 'output_format': 'mp3'}
2026-03-18 22:26:47,568 [INFO] [upload-service] Message published successfully
INFO:     127.0.0.1:57152 - "POST /upload HTTP/1.1" 200 OK

# ------------ converter service
[converter-service] 2026/03/18 22:25:01 Waiting for messages...
[converter-service] 2026/03/18 22:26:47 Processing: 2b623bf8-eb92-4d33-b9c2-c7e9615da1b0
[converter-service] 2026/03/18 22:26:47 Downloading: 2b623bf8-eb92-4d33-b9c2-c7e9615da1b0.mp4
[converter-service] 2026/03/18 22:26:47 Starting conversion: /tmp/2b623bf8-eb92-4d33-b9c2-c7e9615da1b0.mp4
[converter-service] 2026/03/18 22:26:48 Conversion completed: /tmp/2b623bf8-eb92-4d33-b9c2-c7e9615da1b0.mp3
[converter-service] 2026/03/18 22:26:48 Uploading: 2b623bf8-eb92-4d33-b9c2-c7e9615da1b0.mp3
[converter-service] 2026/03/18 22:26:48 Audio ready: 2b623bf8-eb92-4d33-b9c2-c7e9615da1b0.mp3
[converter-service] 2026/03/18 22:26:48 Publishing audio_ready event: {"audio_path":"2b623bf8-eb92-4d33-b9c2-c7e9615da1b0.mp3","video_id":"2b623bf8-eb92-4d33-b9c2-c7e9615da1b0"}

# ------------ notification service
2026-03-18 22:25:55,028 [INFO] [notification-service] Listening for messages on audio_ready...
2026-03-18 22:26:48,427 [INFO] [notification-service] Download ready for video 2b623bf8-eb92-4d33-b9c2-c7e9615da1b0: http://localhost:9000/audios/2b623bf8-eb92-4d33-b9c2-c7e9615da1b0.mp3

```




## Postgres

```sh
docker exec -it postgres psql -U postgres

```

```sql
\l        -- list databases
\c dbname -- connect to a database
\dt       -- list tables
\q        -- quit

-------------------
\c videos
SELECT * FROM videos;
```


## RMQ
RabbitMQ does NOT let you change queue args after creation => you MUST reset queues:
```sh
docker exec -it rabbitmq rabbitmqctl delete_queue video_jobs
docker exec -it rabbitmq rabbitmqctl delete_queue video_jobs_retry
docker exec -it rabbitmq rabbitmqctl delete_queue video_jobs_dlq
```
