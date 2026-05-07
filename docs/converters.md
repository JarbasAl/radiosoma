# mediavocab converters

`radiosoma.converters` — `radiosoma/converters.py`

Translates radiosoma objects into [mediavocab](https://github.com/JarbasAl/mediavocab) types.

## Modelling axioms

- Channel → `Work` with `MediaType.RADIO` (live-linear broadcast).
- Each distinct codec/bitrate encoding → a separate `Release` of that `Work`,
  with `StreamMode.CONTINUOUS`.
- `Work.runtime` is `None` — a continuous broadcast has no finite duration.
- `Work.country = "US"`, `Work.language = "en"` for all SOMA channels.
- `soma_fm_channel_id` (the SOMA short id, e.g. `"groovesalad"`) is stored in
  `Release.external_ids` and `Work.external_ids`.
- Provider modality: `MODALITY = {PlaybackModality.AUDIO}` — `converters.py:37`

## station_to_release(station) -> Release

`radiosoma/converters.py:199`

Returns a single `mediavocab.Release` for the highest-quality stream variant.

```python
from radiosoma import get_stations
from radiosoma.converters import station_to_release

station = next(s for s in get_stations() if s.station_id == "groovesalad")
release = station_to_release(station)

print(release.work.title)            # "Groove Salad"
print(release.work.media_type)       # MediaType.RADIO
print(release.stream_mode)           # StreamMode.CONTINUOUS
print(release.codec, release.bitrate)  # "aac" "130"
print(release.audio_channels)        # "stereo"
print(release.work.content_genres)   # [GENRE_AMBIENT]
print(release.external_ids["soma_fm_channel_id"])  # "groovesalad"
```

If the station has no stream variants, returns an empty `Release` with
`uri=""` so callers always get a valid object.

## station_to_releases(station) -> list[Release]

`radiosoma/converters.py:224`

Returns one `Release` per stream variant (typically four: high-quality AAC,
MP3, low-bitrate HE-AAC, lo-fi HE-AAC). All releases share the same
underlying `Work` instance — consumers can deduplicate by identity.

```python
from radiosoma.converters import station_to_releases

for release in station_to_releases(station):
    print(release.codec, release.bitrate, release.uri)
    # aac    130  https://somafm.com/groovesalad130.pls
    # mp3    256  https://somafm.com/groovesalad256.pls
    # he-aac  64  https://somafm.com/groovesalad64.pls
    # he-aac  32  https://somafm.com/groovesalad32.pls
```

## song_to_programme(song, station) -> Programme | None

`radiosoma/converters.py:237`

Converts a single recent-tracks dict to a `mediavocab.Programme`. Returns
`None` if the entry has no title.

- `programme.work` — `EntityRef` with `name = "Artist - Title"`;
  `external_ids` carries `track_artist` and `track_album` when present.
- `programme.channel` — `EntityRef` carrying `soma_fm_channel_id`.
- `programme.starts_at` — ISO datetime derived from the unix `date` field.
- `programme.is_live = True`, `programme.is_repeat = False`.

## recent_tracks_to_programmes(songs, station) -> list[Programme]

`radiosoma/converters.py:293`

Vectorised `song_to_programme`; filters out entries with empty titles.

## recent_tracks_to_schedule(songs, station) -> Schedule

`radiosoma/converters.py:306`

Wraps the recent-tracks list in a `mediavocab.Schedule`:

- `source = "somafm.com"`
- `fetched_at` — current wall clock (ISO UTC)
- `valid_from` / `valid_until` — min/max of programme `starts_at` timestamps

```python
from radiosoma import get_recent_tracks, get_stations
from radiosoma.converters import recent_tracks_to_schedule

station = next(s for s in get_stations() if s.station_id == "groovesalad")
songs = get_recent_tracks(station.station_id)
schedule = recent_tracks_to_schedule(songs, station)

print(schedule.source)          # "somafm.com"
print(schedule.fetched_at)      # ISO datetime
for prog in schedule.programmes[:3]:
    print(prog.starts_at, prog.work.name)
```

## Genre mapping

SOMA genre strings (comma- or pipe-separated) are tokenised and resolved
against `mediavocab.taxonomy.genre.GENRE_*` constants. Unmapped tokens fall
through as raw lower-cased strings. `radiosoma/converters.py:45`
