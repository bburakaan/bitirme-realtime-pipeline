from faker import Faker
import random
from datetime import datetime, timedelta
from typing import Dict, List

fake = Faker()

CATEGORIES: List[str] = ["electronics", "fashion", "books", "home", "sports"]
DEVICES: List[str] = ["mobile", "desktop", "tablet"]
SOURCES: List[str] = ["home_page", "search_page", "product_page", "category_page"]


def get_profile_event_sequence(profile: str) -> List[str]:
    if profile == "browser":
        return random.choices(
            ["page_view", "click", "search"],
            weights=[50, 35, 15],
            k=random.randint(3, 7)
        )

    if profile == "interested":
        return random.choices(
            ["page_view", "click", "search", "add_to_cart"],
            weights=[35, 30, 15, 20],
            k=random.randint(4, 8)
        )

    if profile == "buyer":
        seq = random.choices(
            ["page_view", "click", "search", "add_to_cart"],
            weights=[25, 30, 10, 35],
            k=random.randint(4, 7)
        )
        seq.append("purchase")
        return seq

    return ["page_view", "click"]


def generate_session_events() -> List[Dict]:
    session_id = fake.uuid4()
    user_id = random.randint(1, 100)
    profile = random.choices(
        ["browser", "interested", "buyer"],
        weights=[50, 30, 20],
        k=1
    )[0]

    event_sequence = get_profile_event_sequence(profile)
    base_time = datetime.now() - timedelta(minutes=random.randint(0, 500))
    current_time = base_time

    events: List[Dict] = []

    for event_type in event_sequence:
        current_time += timedelta(seconds=random.randint(10, 90))

        event = {
            "event_id": fake.uuid4(),
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "product_id": random.randint(1000, 9999),
            "category": random.choice(CATEGORIES),
            "price": round(random.uniform(50, 5000), 2),
            "timestamp": current_time.isoformat(),
            "device_type": random.choice(DEVICES),
            "source": random.choice(SOURCES),
            "profile": profile
        }
        events.append(event)

    return events


if __name__ == "__main__":
    for event in generate_session_events():
        print(event)