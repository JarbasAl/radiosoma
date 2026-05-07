"""Rich mediavocab demo: fetch the Groove Salad channel, emit one
``Release`` per stream variant and a ``Schedule`` of recent tracks."""
from radiosoma import get_recent_tracks, get_stations
from radiosoma.converters import (
    recent_tracks_to_schedule,
    station_to_releases,
)

# Pick a known channel — Groove Salad (downtempo/ambient).
station = next(s for s in get_stations() if s.station_id == "groovesalad")

print(f"Channel: {station.title} [{station.genre}]")
print(f"DJ:      {station.dj}")
print(f"Listeners: {station.listeners}")
print()

# One Release per bitrate/codec variant. All share the same Work.
print("Releases (one per stream variant):")
releases = station_to_releases(station)
for r in releases:
    print(
        f"  codec={r.codec:<7} bitrate={r.bitrate:>4}kbps "
        f"container={r.container:<5} uri={r.uri}"
    )
print(f"  content_genres={releases[0].work.content_genres}")
print(f"  country={releases[0].work.country} language={releases[0].work.language}")
print(f"  runtime={releases[0].work.runtime}  (None = continuous live)")
print()

# Recent-tracks feed → Schedule of Programme entries.
songs = get_recent_tracks(station.station_id)
schedule = recent_tracks_to_schedule(songs, station)
print(f"Schedule (source={schedule.source}, fetched_at={schedule.fetched_at}):")
print(f"  window {schedule.valid_from} → {schedule.valid_until}")
for prog in schedule.programmes[:5]:
    print(
        f"  {prog.starts_at}  {prog.work.name}  "
        f"album={prog.work.external_ids.get('track_album', '')!r}"
    )
