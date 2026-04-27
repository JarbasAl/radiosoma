# radiosoma

Python client for the [SomaFM](https://somafm.com) public channels API.

## Install

```bash
pip install radiosoma
```

## Quick start

```python
from radiosoma import get_stations

for station in get_stations():
    print(station.title, station.best_stream)
```

## Docs

- [API reference](docs/api.md)

## Examples

See the [`examples/`](examples/) directory.
