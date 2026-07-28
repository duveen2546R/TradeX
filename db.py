"""MongoDB Atlas connection and collection indexes for TradeX."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()


client: MongoClient | None = None
database = None


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def init_database():
    """Connect to Atlas and initialise the indexes relied upon by the app."""
    global client, database
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is required. Copy .env.example and configure MongoDB Atlas.")

    client = MongoClient(
        uri,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        retryWrites=True,
        tz_aware=True,
    )
    client.admin.command("ping")
    database = client[os.getenv("MONGODB_DATABASE", "tradex")]
    ensure_indexes(database)
    return database


def get_database():
    if database is None:
        raise RuntimeError("MongoDB has not been initialised.")
    return database


def ensure_indexes(db):
    db.users.create_index("email", unique=True, name="unique_user_email")
    db.portfolios.create_index([("user_id", ASCENDING), ("status", ASCENDING)], name="user_active_portfolio")
    db.orders.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)], name="user_order_history")
    db.watchlists.create_index("user_id", unique=True, name="unique_user_watchlist")
    db.alerts.create_index(
        [("symbol", ASCENDING), ("status", ASCENDING), ("kind", ASCENDING)],
        name="active_alert_lookup",
    )
    db.notifications.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)], name="user_notifications")
    db.market_quotes.create_index("symbol", unique=True, name="unique_quote_symbol")
