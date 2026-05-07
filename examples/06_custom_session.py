"""06 — Inject a custom requests.Session with extra headers.

The same session can be reused across get_stations, get_recent_tracks,
and SomaFmStation to control connection pooling, headers, and timeouts.
"""
import requests
from radiosoma import get_recent_tracks, get_stations

sess = requests.Session()
sess.headers.update({"User-Agent": "my-app/1.0 radiosoma-example"})
sess.timeout = 10  # seconds; requests honours this as a default

stations = list(get_stations(session=sess))
print(f"Fetched {len(stations)} channels with custom session")

# Reuse the same session for recent-tracks.
channel_id = stations[0].station_id
songs = get_recent_tracks(channel_id, session=sess)
print(f"Recent tracks for '{channel_id}': {len(songs)} entries")

# SomaFmStation also accepts a session directly.
from radiosoma import SomaFmStation  # noqa: E402

raw = stations[0].raw
station = SomaFmStation(raw, session=sess)
print(f"Station via injected session: {station.title}  {station.best_stream}")
