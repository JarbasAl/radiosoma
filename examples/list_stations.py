"""List all SomaFM stations with their stream URLs."""
from radiosoma import get_stations

for station in get_stations():
    print(f"{station.title} [{station.genre}]")
    print(f"  best:    {station.best_stream}")
    print(f"  fastest: {station.fastest_stream}")
    print(f"  direct:  {station.direct_stream}")
    print()
