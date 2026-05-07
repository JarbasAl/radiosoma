"""01 — List channels, pick one by id, print its best stream URL."""
from radiosoma import get_stations

stations = list(get_stations())
print(f"Total channels: {len(stations)}")
print()

# Print every channel with its primary stream URL.
for station in stations:
    print(f"{station.station_id:<20} {station.title:<30} {station.best_stream}")

print()

# Pick a specific channel by id.
target = next((s for s in stations if s.station_id == "groovesalad"), None)
if target:
    print(f"Selected: {target.title}")
    print(f"  best_stream:   {target.best_stream}")
    print(f"  direct_stream: {target.direct_stream}")
