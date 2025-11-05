def decide_green_seconds(vehicle_count: int, avg_speed_kmh: float) -> tuple[int, str]:
    if vehicle_count >= 60 or avg_speed_kmh < 15:
        return 70, "Heavy congestion or low speed"
    if vehicle_count >= 45:
        return 55, "Moderate-high load"
    if vehicle_count >= 25:
        return 40, "Moderate"
    return 25, "Low load"
