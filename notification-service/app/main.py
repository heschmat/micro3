from fastapi import FastAPI
import threading

from app.consumer import start_consumer
from app.logger import logger

app = FastAPI(title="Notification Service")

# Run RabbitMQ consumer in separate thread
threading.Thread(target=start_consumer, daemon=True).start()

@app.get("/")
def health():
    return {"status": "ok"}
