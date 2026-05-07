# radiosoma API

`radiosoma` is a thin Python client for the [SomaFM](https://somafm.com) public channels API.

## get_stations()

```python
from radiosoma import get_stations

for station in get_stations():
    print(station.title, station.best_stream)
```

Returns a generator of `SomaFmStation` objects.

## SomaFmStation

### Properties

| Property | Type | Description |
|---|---|---|
| `station_id` | `str` | Short identifier (e.g. `"groovesalad"`) |
| `title` | `str` | Human-readable name |
| `description` | `str` | Station description |
| `genre` | `str` | Music genre tag |
| `image` | `str \| None` | URL of the largest available image |
| `streams` | `list[str]` | All available playlist URLs |
| `best_stream` | `str \| None` | Highest-quality playlist URL |
| `fastest_stream` | `str \| None` | Lowest-latency playlist URL |
| `m3u_stream` | `str` | Constructed `.m3u` URL |
| `direct_stream` | `str` | Direct MP3 stream URL (ice2) |
| `alt_direct_stream` | `str` | Alternate direct MP3 stream (ice4) |

### `__str__` / `__repr__`

`str(station)` returns `fastest_stream` (empty string if unavailable).  
`repr(station)` returns `"<title>:<fastest_stream>"`.

## Stream URL priority

- `best_stream` — prefers `highestpls` entries first, falls back to `fastpls`
- `fastest_stream` — prefers `fastpls` entries first, falls back to `highestpls`
- `direct_stream` / `alt_direct_stream` — always available, constructed from `station_id`

## get_recent_tracks(channel_id)

```python
from radiosoma import get_recent_tracks

for song in get_recent_tracks("groovesalad"):
    print(song["artist"], "-", song["title"])
```

Returns a list of dicts (most recent first) with keys `title`, `artist`,
`album`, `albumart`, `date` (unix epoch as string).

## mediavocab converters

`radiosoma.converters` translates radiosoma data into the canonical
[mediavocab](https://github.com/JarbasAl/mediavocab) types.

### Modality

```python
from radiosoma.converters import MODALITY  # {PlaybackModality.AUDIO}
```

### `station_to_release(station) -> Release`

Returns a `mediavocab.Release` whose:

- `work.media_type == MediaType.RADIO` (axiom 8: a station is a `Work`)
- `stream_mode == StreamMode.CONTINUOUS` (rolling live linear broadcast)
- `work.country == "US"` and `work.language == "en"`
- `work.external_ids["soma_fm_channel_id"]` is the SOMA FM channel id (string)
- `uri` is the best available stream URL
- `image` is the largest channel artwork

### `song_to_programme(song, station) -> Programme | None`

Builds a `mediavocab.Programme` from a single recent-tracks dict. The
programme's `channel` is an `EntityRef` with the channel's
`soma_fm_channel_id`, `is_live=True`, and `starts_at` an ISO datetime
derived from the unix `date` field.

### `recent_tracks_to_programmes(songs, station) -> list[Programme]`

Vectorised form of `song_to_programme`; entries with empty titles are
filtered out.
