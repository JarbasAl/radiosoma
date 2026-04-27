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
