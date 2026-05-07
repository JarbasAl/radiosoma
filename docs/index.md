# radiosoma

Python client for the [SomaFM](https://somafm.com) public channels API,
with [mediavocab](https://github.com/JarbasAl/mediavocab) converters.

## Overview

`radiosoma` fetches the SomaFM channel list and recent-tracks feeds,
wraps them in typed Python objects, and converts them to the canonical
mediavocab vocabulary for use in media-aware applications.

## Key classes

| Class | Purpose | Source |
|---|---|---|
| `SomaFmStation` | Channel object — properties, stream variants, stream URLs | `radiosoma/__init__.py:107` |
| `StreamVariant` | Single bitrate/codec offering for a channel | `radiosoma/__init__.py:84` |

## Key functions

| Function | Purpose | Source |
|---|---|---|
| `get_stations` | Generator of `SomaFmStation` for every live channel | `radiosoma/__init__.py:227` |
| `get_recent_tracks` | Recent-tracks feed as a list of dicts | `radiosoma/__init__.py:238` |
| `station_to_release` | Single mediavocab `Release` (highest-quality stream) | `radiosoma/converters.py:199` |
| `station_to_releases` | One mediavocab `Release` per stream variant | `radiosoma/converters.py:224` |
| `default_session` | Returns the active HTTP session (requests or curl_cffi) | `radiosoma/transport.py:16` |

## Contents

- [Installation & quick start](../README.md#install)
- [Getting started](getting-started.md)
- [API reference](api.md)
- [mediavocab converters](converters.md)
- [HTTP transport](transport.md)
