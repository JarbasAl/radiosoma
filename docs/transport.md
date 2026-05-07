# HTTP transport

`radiosoma/transport.py`

## default_session()

`radiosoma/transport.py:16`

Returns a requests-compatible session. Called automatically by `get_stations`,
`get_recent_tracks`, and `SomaFmStation` when no session is passed.

**Default:** `requests.Session()`

**With `RADIOSOMA_TRANSPORT=curl_cffi`:** returns a `curl_cffi` session
impersonating a recent Chrome browser, if `curl_cffi` is importable.
Falls back to `requests` silently if the package is absent.

## Injecting a custom session

All public functions accept a `session` keyword argument:

```python
import requests
from radiosoma import get_stations, get_recent_tracks

sess = requests.Session()
sess.headers["User-Agent"] = "my-app/1.0"

stations = list(get_stations(session=sess))
songs = get_recent_tracks("groovesalad", session=sess)
```

`SomaFmStation` accepts it too:

```python
from radiosoma import SomaFmStation

station = SomaFmStation(raw_dict, session=sess)
```

## curl_cffi stealth transport

SomaFM is an open, friendly API — stealth transport is not required.
This option exists for consistency with the broader api_clients family.

```bash
pip install radiosoma[stealth]
export RADIOSOMA_TRANSPORT=curl_cffi
```

Once set, `default_session()` returns a `curl_cffi.requests.Session`
impersonating Chrome. Unset `RADIOSOMA_TRANSPORT` to revert to `requests`.
