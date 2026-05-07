# Getting started

## Install

```bash
pip install radiosoma
```

For browser-impersonating transport (optional, not required for SomaFM):

```bash
pip install radiosoma[stealth]
```

## List channels

```python
from radiosoma import get_stations

for station in get_stations():
    print(station.station_id, station.title, station.genre)
```

`get_stations` — `radiosoma/__init__.py:227` — yields one `SomaFmStation` per
channel, parsing `https://api.somafm.com/channels.xml`.

## Pick a stream URL

```python
from radiosoma import get_stations

station = next(s for s in get_stations() if s.station_id == "groovesalad")
print(station.best_stream)   # highest-quality PLS URL
print(station.direct_stream) # always-on MP3 (ice2, 128 kbps)
```

## Fetch recent tracks

```python
from radiosoma import get_recent_tracks

songs = get_recent_tracks("groovesalad")
for s in songs[:5]:
    print(s["artist"], "-", s["title"])
```

`get_recent_tracks` — `radiosoma/__init__.py:238` — returns a list of dicts
with keys `title`, `artist`, `album`, `albumart`, `date`.

## Convert to mediavocab

```python
from radiosoma import get_stations
from radiosoma.converters import station_to_release

station = next(s for s in get_stations() if s.station_id == "groovesalad")
release = station_to_release(station)
print(release.work.title)       # "Groove Salad"
print(release.codec)            # "aac"
print(release.bitrate)          # "130"
print(release.stream_mode)      # StreamMode.CONTINUOUS
```

See [converters.md](converters.md) for the full converter API.
