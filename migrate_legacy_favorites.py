"""Import the previous shared favorites.json into one existing TradeX account."""
from __future__ import annotations

import argparse
import json
import os

from db import init_database, utcnow


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True, help="Existing account that will own the legacy watchlist")
    parser.add_argument("--file", default="favorites.json")
    args = parser.parse_args()

    db = init_database()
    user = db.users.find_one({"email": args.email.strip().lower()})
    if not user:
        raise SystemExit("No user exists for that email. Register the account first.")
    with open(args.file, "r", encoding="utf-8") as source:
        legacy = json.load(source)
    symbols = sorted(set(legacy.get("1", [])))
    db.watchlists.update_one(
        {"user_id": str(user["_id"])},
        {"$set": {"symbols": symbols, "updated_at": utcnow()}},
        upsert=True,
    )
    print(f"Imported {len(symbols)} favorites for {args.email}.")


if __name__ == "__main__":
    main()
