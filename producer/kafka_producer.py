import json
import os
import time

from dotenv import load_dotenv
from kafka import KafkaProducer

from producer.event_generator import generate_session_events

load_dotenv()

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "user-events")
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")


def create_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )


def main() -> None:
    producer = create_producer()
    print(f"Sending session events to Kafka topic: {KAFKA_TOPIC}")

    try:
        while True:
            session_events = generate_session_events()

            for event in session_events:
                producer.send(KAFKA_TOPIC, event)
                print(f"Sent: {event}")

            producer.flush()
            time.sleep(2)

    except KeyboardInterrupt:
        print("Producer stopped.")
    finally:
        producer.close()


if __name__ == "__main__":
    main()