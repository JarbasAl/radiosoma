"""Converters from radiosoma models to mediavocab typed objects.

SOMA FM channels are modelled per mediavocab axiom 8:

* Each channel is a ``Work`` with ``MediaType.RADIO`` (live-linear broadcast).
* Each stream URL is a ``Release`` with ``StreamMode.CONTINUOUS``.
* Audio-only providers declare ``modality = {PlaybackModality.AUDIO}``.

Recent-tracks feeds (``https://somafm.com/songs/<id>.xml``) are surfaced as
``Programme`` entries scheduled against the channel ``Work``.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from mediavocab import (
    MediaType,
    PlaybackModality,
    Release as MvRelease,
    StreamMode,
    Work,
)
from mediavocab.models.entity import EntityKind, EntityRef
from mediavocab.models.work import Programme

from radiosoma import SomaFmStation


# Audio-only provider axis. Importable by consumers that need to reason
# about the provider modality without instantiating a converter.
MODALITY = {PlaybackModality.AUDIO}


def _channel_ref(station: SomaFmStation) -> EntityRef:
    """Build an ``EntityRef`` pointing at the channel ``Work``."""
    ext: dict = {}
    if station.station_id:
        ext["soma_fm_channel_id"] = str(station.station_id)
    return EntityRef(
        name=station.title,
        kind=EntityKind.SERIES,
        external_ids=ext,
    )


def station_to_release(station: SomaFmStation) -> MvRelease:
    """Convert a :class:`SomaFmStation` to a mediavocab :class:`Release`.

    The returned ``Release`` wraps a ``Work`` whose ``media_type`` is
    ``RADIO`` and whose ``stream_mode`` is ``CONTINUOUS`` (rolling live
    linear broadcast). ``country='US'`` and ``language='en'`` reflect that
    SOMA FM is a US English-language broadcaster.
    """
    content_genres: List[str] = []
    if station.genre:
        if isinstance(station.genre, list):
            content_genres = [g.lower() for g in station.genre if g]
        else:
            content_genres = [
                g.strip().lower()
                for g in str(station.genre).split(",")
                if g.strip()
            ]

    extra: dict = {}
    if station.streams:
        extra["stream_urls"] = station.streams
    if station.description:
        extra["description"] = station.description

    external_ids: dict = {}
    if station.station_id:
        # axiom 8: channel id is a stable external identifier on the Work.
        external_ids["soma_fm_channel_id"] = str(station.station_id)

    work = Work(
        title=station.title,
        media_type=MediaType.RADIO,
        country="US",
        language="en",
        content_genres=content_genres,
        external_ids=dict(external_ids),
        extra=extra,
    )
    uri = station.best_stream or station.fastest_stream or ""
    return MvRelease(
        work=work,
        uri=uri,
        image=station.image or "",
        stream_mode=StreamMode.CONTINUOUS,
        external_ids=dict(external_ids),
        extra=extra,
    )


def song_to_programme(
    song: dict,
    station: SomaFmStation,
) -> Optional[Programme]:
    """Convert a recent-tracks entry to a mediavocab :class:`Programme`.

    ``song`` is a raw dict scraped from ``https://somafm.com/songs/<id>.xml``
    with keys ``title``, ``artist``, ``album``, ``date`` (unix epoch as str).
    Returns ``None`` if the entry has no playable title.
    """
    title = (song.get("title") or "").strip()
    if not title:
        return None

    artist = (song.get("artist") or "").strip()
    name = f"{artist} - {title}" if artist else title

    track_extra: dict = {}
    if song.get("album"):
        track_extra["album"] = song["album"]
    if artist:
        track_extra["artist"] = artist

    work_ref = EntityRef(
        name=name,
        kind=EntityKind.OTHER,
    )

    starts_at: str
    raw_date = song.get("date")
    try:
        starts_at = (
            datetime.fromtimestamp(int(raw_date), tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "+00:00")
        )
    except (TypeError, ValueError):
        starts_at = datetime.now(tz=timezone.utc).isoformat()

    return Programme(
        work=work_ref,
        channel=_channel_ref(station),
        starts_at=starts_at,
        is_live=True,
        extra=track_extra,
    )


def recent_tracks_to_programmes(
    songs: list,
    station: SomaFmStation,
) -> List[Programme]:
    """Vectorised :func:`song_to_programme` for a list of song dicts."""
    out: List[Programme] = []
    for s in songs or []:
        prog = song_to_programme(s, station)
        if prog is not None:
            out.append(prog)
    return out
