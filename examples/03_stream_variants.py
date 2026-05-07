"""03 — Show all stream formats and bitrates for every channel."""
from radiosoma import get_stations

for station in get_stations():
    variants = station.stream_variants
    print(f"{station.title} [{station.genre}]  ({len(variants)} variants)")
    for v in variants:
        print(
            f"  source={v.source:<12} format={v.format:<5} "
            f"codec={v.codec:<7} bitrate={v.bitrate:>4}kbps  {v.url}"
        )
    # Always-available constructed URLs (no PLS lookup required).
    print(f"  direct_stream:     {station.direct_stream}")
    print(f"  alt_direct_stream: {station.alt_direct_stream}")
    print(f"  m3u_stream:        {station.m3u_stream}")
    print()
