from __future__ import annotations

import argparse

from .main import run_etl
from .scheduler import schedule_daily_run


def main() -> None:
    parser = argparse.ArgumentParser(description="ETL Raptor CLI")
    parser.add_argument("--run", action="store_true", help="Run ETL now")
    parser.add_argument("--schedule", action="store_true", help="Start daily scheduler")
    parser.add_argument("--schedule-time", default="00:00", help="Schedule time for daily ETL (HH:MM)")
    args = parser.parse_args()

    if args.run:
        run_etl()
    if args.schedule:
        schedule_daily_run(args.schedule_time)
