"""Find stations matching a genre or name keyword."""
import sys
from radiosoma import get_stations

keyword = sys.argv[1] if len(sys.argv) > 1 else "ambient"

for station in get_stations():
    if keyword.lower() in (station.title + " " + (station.genre or "") + " " + station.description).lower():
        print(repr(station))
        print(f"  {station.description}")
        print()
