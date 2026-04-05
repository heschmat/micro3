import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.consumer import consumer_state, start_consumer


consumer_thread: threading.Thread | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global consumer_thread

    consumer_thread = threading.Thread(
        target=start_consumer,
        name="rabbitmq-consumer",
        daemon=True,
    )
    consumer_thread.start()

    yield


app = FastAPI(title="Notification Service", lifespan=lifespan)


@app.get("/")
def health():
    state = consumer_state.snapshot()

    if not state["running"]:
        raise HTTPException(
            status_code=503,
            detail={"status": "consumer_not_running", **state},
        )

    if not state["connected"]:
        raise HTTPException(
            status_code=503,
            detail={"status": "degraded", **state},
        )

    return {"status": "ok", **state}
