import os
from datetime import datetime

import redis
from sqlalchemy import Column, DateTime, Float, Integer, MetaData, Table, create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/demo")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

metadata = MetaData()

# Old counter table (keeping for reference)
counter_table = Table(
    "counter",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("value", Integer, nullable=False, default=0),
)

# New events table for storing processed events
events_table = Table(
    "events",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("value", Float, nullable=False),
    Column("processed_at", DateTime, nullable=False, default=datetime.utcnow),
)

metadata.create_all(engine)

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
r = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
