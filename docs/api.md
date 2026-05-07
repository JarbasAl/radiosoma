# API reference

## get_stations(session=None)

`radiosoma/__init__.py:227`

```python
from radiosoma import get_stations

for station in get_stations():
    print(station.title, station.best_stream)
```

Generator. Fetches `https://api.somafm.com/channels.xml` and yields one
`SomaFmStation` per channel. Pass `session` to reuse an existing HTTP session.

---

## get_recent_tracks(channel_id, session=None)

`radiosoma/__init__.py:238`

```python
from radiosoma import get_recent_tracks

songs = get_recent_tracks("groovesalad")
# [{"title": ..., "artist": ..., "album": ..., "albumart": ..., "date": "1715000000"}, ...]
```

Returns a list of dicts (most recent first). `date` is a unix epoch string.
Fetches `https://somafm.com/songs/<channel_id>.xml`.

---

## SomaFmStation

`radiosoma/__init__.py:107`

### Properties

| Property | Type | Source line |
|---|---|---|
| `station_id` | `str` | `__init__.py:113` |
| `title` | `str` | `__init__.py:117` |
| `description` | `str` | `__init__.py:129` |
| `genre` | `str \| None` | `__init__.py:133` |
| `image` | `str \| None` | `__init__.py:121` — prefers `xlimage` > `largeimage` > `image` |
| `dj` | `str` | `__init__.py:136` |
| `listeners` | `int \| None` | `__init__.py:140` |
| `last_playing` | `str` | `__init__.py:147` |
| `updated` | `int \| None` | `__init__.py:152` |
| `stream_variants` | `list[StreamVariant]` | `__init__.py:178` — highestpls → fastpls → slowpls |
| `streams` | `list[str]` | `__init__.py:188` — all URLs (legacy) |
| `best_stream` | `str \| None` | `__init__.py:193` — first highestpls, fallback fastpls/slowpls |
| `fastest_stream` | `str \| None` | `__init__.py:199` — first fastpls, fallback highestpls/slowpls |
| `m3u_stream` | `str` | `__init__.py:210` — `http://somafm.com/m3u/<id>.m3u` |
| `direct_stream` | `str` | `__init__.py:214` — `http://ice2.somafm.com/<id>-128-mp3` |
| `alt_direct_stream` | `str` | `__init__.py:218` — `http://ice4.somafm.com/<id>-128-mp3` |

---

## StreamVariant

`radiosoma/__init__.py:84`

| Attribute | Type | Description |
|---|---|---|
| `url` | `str` | Playlist URL |
| `format` | `str` | SOMA format tag: `aac`, `aacp`, `mp3` |
| `bitrate` | `str` | kbps parsed from the playlist filename |
| `codec` | `str` | Canonical codec: `aac`, `he-aac`, `mp3` |
| `container` | `str` | Canonical container: `adts`, `mp3` |
| `source` | `str` | `"highestpls"`, `"fastpls"`, or `"slowpls"` |

`codec` and `container` are derived properties — `radiosoma/__init__.py:96-101`.

### Codec / format mapping

| SOMA `format` | `codec` | `container` |
|---|---|---|
| `aac` | `aac` | `adts` |
| `aacp` | `he-aac` | `adts` |
| `mp3` | `mp3` | `mp3` |

### Bitrate parsing

The bitrate is extracted from the trailing digits of the playlist filename
(`groovesalad130.pls` → `"130"`). Playlists with no numeric suffix default
to `"128"` (legacy MP3 stream). `radiosoma/__init__.py:54`
