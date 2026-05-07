# radiosoma

Python client for the [SomaFM](https://somafm.com) public channels API,
with [mediavocab](https://github.com/JarbasAl/mediavocab) converters.

## Install

```bash
pip install radiosoma
```

Optional stealth transport (rarely needed — SomaFM is an open, friendly API):

```bash
pip install radiosoma[stealth]
```

## Quick start

```python
from radiosoma import get_stations

for station in get_stations():
    print(station.title, station.best_stream)
```

## Public API

| Symbol | Where | What it does |
|---|---|---|
| `get_stations(session=None)` | `radiosoma` | Generator of `SomaFmStation` for every live channel |
| `get_recent_tracks(channel_id, session=None)` | `radiosoma` | List of dicts from the recent-tracks feed (most recent first) |
| `SomaFmStation` | `radiosoma` | Channel object — properties, stream variants, stream URLs |
| `station_to_release(station)` | `radiosoma.converters` | Single `mediavocab.Release` for the highest-quality stream |
| `station_to_releases(station)` | `radiosoma.converters` | One `Release` per bitrate/codec variant |

## Stream variants

Each channel exposes multiple bitrate/codec variants via three PLS playlist sources:

| Source key | Typical variants |
|---|---|
| `highestpls` | 130 kbps AAC, 256 kbps MP3 |
| `fastpls` | 64 kbps HE-AAC |
| `slowpls` | 32 kbps HE-AAC |

```python
for variant in station.stream_variants:
    print(variant.codec, variant.bitrate, variant.url)
    # e.g.  aac     130  https://somafm.com/groovesalad130.pls
    #       mp3     256  https://somafm.com/groovesalad256.pls
    #       he-aac   64  https://somafm.com/groovesalad64.pls
    #       he-aac   32  https://somafm.com/groovesalad32.pls
```

`station.direct_stream` and `station.alt_direct_stream` are always-available
constructed URLs (`ice2`/`ice4`, 128 kbps MP3) that bypass the PLS lookup.

## mediavocab integration

SOMA channels map to mediavocab types:

- Channel → `Work` with `MediaType.RADIO`, `StreamMode.CONTINUOUS`
- Each codec/bitrate variant → a separate `Release` of the same `Work`
- `soma_fm_channel_id` is stored in `Release.external_ids` and `Work.external_ids`
- Recent-tracks feed → `Schedule` of `Programme` entries

```python
from radiosoma import get_stations
from radiosoma.converters import station_to_releases

jazz = next(s for s in get_stations() if s.station_id == "groovesalad")
for release in station_to_releases(jazz):
    print(release.codec, release.bitrate, release.work.title)
```

See [docs/converters.md](docs/converters.md) for the full converter reference.

## HTTP transport

`radiosoma` uses `requests.Session` by default. Inject your own:

```python
import requests
from radiosoma import get_stations

sess = requests.Session()
sess.headers["User-Agent"] = "my-app/1.0"
for station in get_stations(session=sess):
    ...
```

Set `RADIOSOMA_TRANSPORT=curl_cffi` (with `radiosoma[stealth]` installed) to
use a browser-impersonating session. SomaFM does not require this — it exists
for consistency across the api_clients family. See [docs/transport.md](docs/transport.md).

## Docs

- [Getting started](docs/getting-started.md)
- [API reference](docs/api.md)
- [mediavocab converters](docs/converters.md)
- [HTTP transport](docs/transport.md)

## Examples

| File | What it shows |
|---|---|
| [`examples/01_quickstart.py`](examples/01_quickstart.py) | List channels, pick one, print stream URL |
| [`examples/02_recent_tracks.py`](examples/02_recent_tracks.py) | Fetch and print the recent-tracks feed |
| [`examples/03_stream_variants.py`](examples/03_stream_variants.py) | All formats and bitrates for a channel |
| [`examples/04_to_mediavocab.py`](examples/04_to_mediavocab.py) | `Release` shape walk-through |
| [`examples/05_variant_fanout.py`](examples/05_variant_fanout.py) | `station_to_releases` — one Release per variant |
| [`examples/06_custom_session.py`](examples/06_custom_session.py) | Pluggable session / custom headers |

## License

Apache 2.0
