import time, random, requests
from datetime import datetime, timezone
from config import API_URL, API_KEY, JUNCTIONS, TICK_SECONDS

def generate_reading(junction_id: str):
    base = random.choice([10, 20, 30, 40])
    rush_bonus = random.randint(0, 35)
    vehicle_count = max(0, base + rush_bonus + random.randint(-5, 5))
    avg_speed = max(5.0, 50 - vehicle_count * 0.5 + random.uniform(-2, 2))
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "junction_id": junction_id,
        "vehicle_count": int(vehicle_count),
        "avg_speed_kmh": round(avg_speed, 1)
    }

def main():
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    print("🚦 Simulator started... sending traffic data every", TICK_SECONDS, "seconds.\n")
    while True:
        for j in JUNCTIONS:
            payload = generate_reading(j)
            try:
                r = requests.post(API_URL, json=payload, headers=headers, timeout=5)
                if r.status_code == 200:
                    decision = r.json().get("decision", {})
                    print(f"[{payload['junction_id']}] Vehicles={payload['vehicle_count']}, "
                          f"Speed={payload['avg_speed_kmh']} -> Green={decision.get('green_seconds')}s")
                else:
                    print("❌ API Error:", r.status_code, r.text)
            except Exception as e:
                print("❌ Connection failed:", e)
        time.sleep(TICK_SECONDS)

if __name__ == "__main__":
    main()
