import redis
import csv
from datetime import timedelta

# Connect to Redis (adjust host/port/db if needed)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# TTL in seconds (30 minutes)
TTL_SECONDS = 30 * 60

def update_aircraft_record(hex_ident, row, headers):

    updates = {}

    # Map row values to headers
    for i, value in enumerate(row):
        if value != "":
            field = headers[i]
            updates[field] = value

    key = f"experiment_aircraft:{hex_ident}"

    if updates:
        r.hset(key, mapping=updates)
        r.expire(key, TTL_SECONDS)


def parse_sbs_line(line):

    reader = csv.reader([line])
    row = next(reader)
    return row

# Example usage with streamed SBS messages
headers = [
    "message_type", "transmission_type", "session_id", "aircraft_id", "hex_ident",
    "flight_id", "generated_date", "generated_time", "logged_date", "logged_time",
    "callsign", "altitude", "ground_speed", "track", "latitude", "longitude",
    "vertical_rate", "squawk", "alert", "emergency", "spi", "is_on_ground"
]

# Simulated loop (replace with live source)
with open("filtered.csv", "r") as f:

    for line in f:

        if not line.strip().startswith("MSG"):
            continue  # Skip headers or unrelated lines

        row = parse_sbs_line(line)
        hex_ident = row[4]

        if hex_ident == "A842E7":
            update_aircraft_record(hex_ident, row, headers)
