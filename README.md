# radiosoma

Python client for the [SomaFM](https://somafm.com) public channels API,
modelled with [mediavocab](https://github.com/JarbasAl/mediavocab) as the
canonical media vocabulary.

## Install

```bash
pip install radiosoma
```

## Modelling

SOMA FM channels follow mediavocab axiom 8:

* Each channel is a `Work` with `MediaType.RADIO` (live-linear broadcast).
* Each stream URL is a `Release` with `StreamMode.CONTINUOUS`.
* The provider is audio-only (`PlaybackModality.AUDIO`).
* The recent-tracks feed surfaces as a list of `Programme` entries pointing
  at the channel `Work`.

## Quick start

```python
from radiosoma import get_stations

for station in get_stations():
    print(station.title, station.best_stream)
```

## Convert to mediavocab

```python
from radiosoma import get_stations
from radiosoma.converters import station_to_release

# fetch the soma jazz channel
jazz = next(s for s in get_stations() if s.station_id == "groovesalad")

release = station_to_release(jazz)
print(release.work.title)             # "Groove Salad"
print(release.work.media_type)        # MediaType.RADIO
print(release.stream_mode)            # StreamMode.CONTINUOUS
print(release.work.country)           # "US"
print(release.work.language)          # "en"
print(release.work.external_ids["soma_fm_channel_id"])  # "groovesalad"
print(release.uri)                    # https://ice.somafm.com/groovesalad-...
```

## Now-playing / recent tracks

```python
from radiosoma import get_recent_tracks, get_stations
from radiosoma.converters import recent_tracks_to_programmes

jazz = next(s for s in get_stations() if s.station_id == "groovesalad")
songs = get_recent_tracks("groovesalad")
programmes = recent_tracks_to_programmes(songs, jazz)

now_playing = programmes[0]
print(now_playing.work.name)          # "Artist - Title"
print(now_playing.channel.external_ids["soma_fm_channel_id"])
print(now_playing.starts_at)          # ISO datetime with offset
```

## Provider modality axis

```python
from radiosoma.converters import MODALITY
from mediavocab import PlaybackModality

assert MODALITY == {PlaybackModality.AUDIO}
```

## Docs

- [API reference](docs/api.md)

## Examples

See the [`examples/`](examples/) directory.
