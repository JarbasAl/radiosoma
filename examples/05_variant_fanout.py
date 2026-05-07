"""05 — station_to_releases: one mediavocab Release per stream variant.

All releases share the same underlying Work object — check with `is`.
"""
from radiosoma import get_stations
from radiosoma.converters import station_to_releases

station = next(s for s in get_stations() if s.station_id == "groovesalad")
releases = station_to_releases(station)

print(f"Channel: {station.title}  ({len(releases)} releases)\n")

for r in releases:
    print(
        f"  codec={r.codec:<7} bitrate={r.bitrate:>4}kbps "
        f"container={r.container:<5} uri={r.uri}"
    )

print()

# All releases share the same Work instance.
works = [r.work for r in releases]
assert all(w is works[0] for w in works), "Work instances differ"
print(f"All {len(releases)} releases share the same Work: {works[0].title!r}")
print(f"soma_fm_channel_id: {releases[0].external_ids.get('soma_fm_channel_id')}")
