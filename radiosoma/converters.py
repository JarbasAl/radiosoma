"""Converters from radiosoma models to mediavocab typed objects."""
from __future__ import annotations

from mediavocab import (
    MediaType,
    Release as MvRelease,
    StreamMode,
    Work,
)

from radiosoma import SomaFmStation


def station_to_release(station: SomaFmStation) -> MvRelease:
    """Convert a ``SomaFmStation`` to a mediavocab ``Release``."""
    content_genres = []
    if station.genre:
        # genre may be a comma-separated string or a list
        if isinstance(station.genre, list):
            content_genres = [g.lower() for g in station.genre if g]
        else:
            content_genres = [g.strip().lower() for g in str(station.genre).split(",") if g.strip()]

    extra: dict = {}
    if station.streams:
        extra["stream_urls"] = station.streams
    if station.description:
        extra["description"] = station.description

    external_ids: dict = {}
    if station.station_id:
        external_ids["somafm_id"] = station.station_id

    work = Work(
        title=station.title,
        media_type=MediaType.RADIO,
        content_genres=content_genres,
        external_ids=external_ids,
        extra=extra,
    )
    uri = station.best_stream or station.fastest_stream or ""
    return MvRelease(
        work=work,
        uri=uri,
        image=station.image or "",
        stream_mode=StreamMode.CONTINUOUS,
        external_ids=external_ids,
        extra=extra,
    )
