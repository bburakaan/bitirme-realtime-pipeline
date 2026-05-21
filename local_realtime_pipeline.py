import argparse
import subprocess
import sys


COMMANDS = {
    "api": [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"],
    "producer": [sys.executable, "-m", "producer.kafka_producer"],
    "consumer": [sys.executable, "-m", "consumer.session_feature_consumer"],
    "raw-consumer": [sys.executable, "-m", "consumer.kafka_consumer"],
    "demo-worker": [sys.executable, "-m", "producer.db_demo_worker"],
    "init-db": [sys.executable, "-m", "db.init_db"],
    "train-intent": [sys.executable, "-m", "ml.train_intent_model"],
    "train-session": [sys.executable, "-m", "ml.train_model"],
    "export-session-data": [sys.executable, "-m", "ml.prepare_dataset"],
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one component of the realtime e-commerce pipeline."
    )
    parser.add_argument(
        "component",
        choices=sorted(COMMANDS),
        help="Component command to run.",
    )
    args = parser.parse_args()

    command = COMMANDS[args.component]
    print(f"Running: {' '.join(command)}")
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
