import json
import os
from collections import Counter
from datetime import datetime

from dotenv import load_dotenv
from kafka import KafkaConsumer

load_dotenv()

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "user-events")
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "user-events-consumer")

OUTPUT_FILE = "data/kafka_events.jsonl"


def ensure_output_dir() -> None:
    os.makedirs("data", exist_ok=True)


def create_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )


def append_event_to_file(event: dict) -> None:
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def main() -> None:
    ensure_output_dir()
    consumer = create_consumer()

    print(f"Listening Kafka topic: {KAFKA_TOPIC}")
    print(f"Saving events to: {OUTPUT_FILE}")
    print("Press Ctrl+C to stop.\n")

    event_counter = Counter()
    total_count = 0

    try:
        for message in consumer:
            event = message.value
            append_event_to_file(event)

            event_type = event.get("event_type", "unknown")
            event_counter[event_type] += 1
            total_count += 1

            print(f"[{datetime.now().isoformat()}] Received event #{total_count}")
            print(f"event_type : {event_type}")
            print(f"user_id    : {event.get('user_id')}")
            print(f"session_id : {event.get('session_id')}")
            print(f"profile    : {event.get('profile')}")
            print(f"counts     : {dict(event_counter)}")
            print("-" * 50)

    except KeyboardInterrupt:
        print("\nConsumer stopped by user.")
        print(f"Total events consumed: {total_count}")
        print(f"Event type distribution: {dict(event_counter)}")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()