"""
run_scheduler.py
================
Local scheduler to trigger the full ingest pipeline:
  Phase 1 → Scrape fund pages (phase_1_ingestion/scraper.py)
  Phase 2 → Chunk & index into ChromaDB (phase_2_indexing/ingestion.py)

Usage:
  python run_scheduler.py           # Run once immediately, then schedule daily at 09:15 IST
  python run_scheduler.py --once    # Run once and exit (useful for debugging)
  python run_scheduler.py --time HH:MM  # Override the daily schedule time (24h, system local time)

Logs are written to: logs/scheduler.log
"""

import sys
import os
import time
import logging
import schedule
import argparse
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure the project root is on the Python path so src.* imports work
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Logging Setup — both file (logs/scheduler.log) and console
# ---------------------------------------------------------------------------
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "scheduler.log"

log_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# File handler — append mode so history is preserved across runs
file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Root logger
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])

logger = logging.getLogger("scheduler")

# ---------------------------------------------------------------------------
# Phase runners
# ---------------------------------------------------------------------------

def run_phase_1() -> bool:
    """Run the scraping job from phase_1_ingestion/scraper.py."""
    logger.info("=" * 60)
    logger.info("PHASE 1 -- Scraping: START")
    logger.info("=" * 60)
    start = datetime.now()

    try:
        from src.phase_1_ingestion.scraper import run_scraping_job

        run_scraping_job()

        elapsed = (datetime.now() - start).total_seconds()
        logger.info(f"PHASE 1 -- Scraping: COMPLETE  (elapsed: {elapsed:.1f}s)")
        return True

    except Exception as exc:
        elapsed = (datetime.now() - start).total_seconds()
        logger.exception(f"PHASE 1 -- Scraping: FAILED after {elapsed:.1f}s  -> {exc}")
        return False


def run_phase_2() -> bool:
    """Run the ingestion/indexing job from phase_2_indexing/ingestion.py."""
    logger.info("=" * 60)
    logger.info("PHASE 2 -- Indexing: START")
    logger.info("=" * 60)
    start = datetime.now()

    try:
        from src.phase_2_indexing.ingestion import run_ingestion

        run_ingestion()

        elapsed = (datetime.now() - start).total_seconds()
        logger.info(f"PHASE 2 -- Indexing: COMPLETE  (elapsed: {elapsed:.1f}s)")
        return True

    except Exception as exc:
        elapsed = (datetime.now() - start).total_seconds()
        logger.exception(f"PHASE 2 -- Indexing: FAILED after {elapsed:.1f}s  -> {exc}")
        return False


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def run_pipeline():
    """Execute Phase 1 -> Phase 2 sequentially and log a summary."""
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"  PIPELINE RUN  [{run_id}]")
    logger.info("=" * 60)

    results = {}

    # Phase 1 -- Scraper
    results["phase_1_scraping"] = run_phase_1()

    # Phase 2 -- Ingestion (always attempt even if phase 1 partially failed,
    # because existing raw data may already be present)
    results["phase_2_indexing"] = run_phase_2()

    # Summary
    logger.info("")
    logger.info("-- Pipeline Summary " + "-" * 40)
    for phase, ok in results.items():
        status = "[OK]" if ok else "[FAILED]"
        logger.info(f"  {phase:<25} {status}")
    overall = all(results.values())
    logger.info(f"  Overall status: {'SUCCESS' if overall else 'PARTIAL / FAILED'}")
    logger.info(f"  Log file: {LOG_FILE}")
    logger.info("-" * 60)
    logger.info("")

    return overall


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Local ingest scheduler for the Mutual Fund RAG pipeline."
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run the pipeline once and exit (skip the scheduler loop).",
    )
    parser.add_argument(
        "--time",
        metavar="HH:MM",
        default="09:15",
        help="Daily schedule time in 24-hour format (default: 09:15). "
             "Uses your system's local clock.",
    )
    args = parser.parse_args()

    logger.info(f"run_scheduler.py started  |  args={sys.argv[1:]}")
    logger.info(f"Project root : {PROJECT_ROOT}")
    logger.info(f"Log file     : {LOG_FILE}")

    # Always do an immediate run first
    success = run_pipeline()

    if args.once:
        logger.info("--once flag detected. Exiting after single run.")
        sys.exit(0 if success else 1)

    # Schedule daily recurring runs
    schedule_time = args.time
    schedule.every().day.at(schedule_time).do(run_pipeline)

    logger.info(f"Scheduler active. Next run scheduled at {schedule_time} (local time).")
    logger.info("Press Ctrl+C to stop.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # check every 30 seconds

    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user (KeyboardInterrupt).")
        sys.exit(0)


if __name__ == "__main__":
    main()
