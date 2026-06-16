from __future__ import annotations

import argparse

from app.config import get_settings
from app.db import EventStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Calendar Maker administration")
    parser.add_argument("command", choices=["create-invite"])
    args = parser.parse_args()

    store = EventStore(get_settings().database_path)
    store.init()
    if args.command == "create-invite":
        print(store.create_invite())


if __name__ == "__main__":
    main()
