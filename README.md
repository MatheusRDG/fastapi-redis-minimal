# FastAPI + Redis Event Stream

A minimal producer-consumer demo using **Redis as a message broker** and **Postgres for persistence**.

## 🎯 What it does

- **Producer**: Generates 10 random numbers/second → pushes to Redis list
- **Redis Queue**: Buffers events in memory (fast, handles bursts)
- **Consumer**: Background task reads from Redis → batch writes to Postgres (every 5 seconds)
- **Real-time UI**: Live stats showing queue size, events produced, and events processed

## 🚀 Run

```bash
docker-compose up --build
```

Open: **http://localhost:8000**

## 🎮 Usage

1. Click **Start Producer** → generates 10 events/sec
2. Watch **Queue Size** grow in Redis
3. Consumer automatically processes batches → saves to Postgres
4. Click **Process Batch Now** for manual processing
5. Click **Stop Producer** to pause

## 🧠 Key Concepts

- **Decoupling**: Producer and consumer run independently
- **Buffering**: Redis absorbs traffic spikes without overwhelming Postgres
- **Batching**: Efficient bulk inserts (50-100 events per batch)
- **Durability trade-off**: Fast writes to Redis (memory) → eventual persistence to Postgres (disk)

## 📦 Stack

- FastAPI (async web framework)
- Redis (in-memory queue)
- PostgreSQL (persistent storage)
- Docker Compose (orchestration)

## 📂 Project Structure

```
app/
  ├── main.py        # API routes & producer/consumer logic
  ├── db.py          # Database & Redis connections
  └── templates/
      └── index.html # Real-time monitoring UI
```
