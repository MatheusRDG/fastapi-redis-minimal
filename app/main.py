import asyncio
import json
import random
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db import SessionLocal, events_table, r

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Global flag to control producer
producer_running = False

# Constants
EVENTS_QUEUE = "events_queue"
STATS_TOTAL = "stats:total_produced"
STATS_PROCESSED = "stats:total_processed"


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/stats")
def get_stats():
    """Get real-time statistics from Redis"""
    queue_size = r.llen(EVENTS_QUEUE)
    total_produced = int(r.get(STATS_TOTAL) or 0)
    total_processed = int(r.get(STATS_PROCESSED) or 0)

    return {
        "queue_size": queue_size,
        "total_produced": total_produced,
        "total_processed": total_processed,
        "in_redis": queue_size,
    }


@app.post("/producer/start")
async def start_producer(background_tasks: BackgroundTasks):
    """Start the event producer"""
    global producer_running
    if producer_running:
        return {"status": "already_running"}

    producer_running = True
    background_tasks.add_task(produce_events)
    return {"status": "started"}


@app.post("/producer/stop")
def stop_producer():
    """Stop the event producer"""
    global producer_running
    producer_running = False
    return {"status": "stopped"}


@app.post("/consumer/process")
async def process_batch(background_tasks: BackgroundTasks):
    """Manually trigger batch processing"""
    background_tasks.add_task(consume_events_batch)
    return {"status": "processing"}


async def produce_events():
    """Background task: Produce 10 events per second"""
    while producer_running:
        try:
            # Generate 10 random numbers
            for _ in range(10):
                event = {
                    "value": round(random.uniform(0, 100), 2),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                # Push to Redis list (left push = queue)
                r.lpush(EVENTS_QUEUE, json.dumps(event))
                r.incr(STATS_TOTAL)

            # Wait 1 second before next batch
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Producer error: {e}")
            break


async def consume_events_batch(batch_size: int = 50):
    """Background task: Consume events from Redis and write to Postgres in batches"""
    try:
        db = SessionLocal()
        batch = []

        # Pull up to batch_size events from Redis
        for _ in range(batch_size):
            event_json = r.rpop(EVENTS_QUEUE)  # Right pop (FIFO)
            if not event_json:
                break

            event = json.loads(event_json)
            batch.append(
                {
                    "value": event["value"],
                    "processed_at": datetime.utcnow(),
                }
            )

        # Batch insert to Postgres
        if batch:
            db.execute(events_table.insert(), batch)
            db.commit()
            r.incrby(STATS_PROCESSED, len(batch))
            print(f"✅ Processed {len(batch)} events to Postgres")

        db.close()
    except Exception as e:
        print(f"Consumer error: {e}")


@app.on_event("startup")
async def startup_event():
    """Start background consumer on app startup"""
    asyncio.create_task(background_consumer())


async def background_consumer():
    """Continuously consume events every 5 seconds"""
    while True:
        await asyncio.sleep(5)  # Process every 5 seconds
        await consume_events_batch(batch_size=100)
