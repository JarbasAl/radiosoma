"""Converters from radiosoma models to mediavocab typed objects.

SOMA FM channels are modelled per mediavocab axiom 8:

* Each channel is a ``Work`` with ``MediaType.RADIO`` (live-linear broadcast).
* Each distinct stream encoding is a ``Release`` with
  ``StreamMode.CONTINUOUS``. SOMA exposes multiple bitrate/codec pairs
  per channel (e.g. 130 kbps AAC, 128 kbps MP3, 64 kbps HE-AAC,
  32 kbps HE-AAC); each is a separate ``Release`` of the same ``Work``.
* Audio-only providers declare ``modality = {PlaybackType.AUDIO}``.

Recent-tracks feeds (``https://somafm.com/songs/<id>.xml``) are surfaced as
``Programme`` entries scheduled against the channel ``Work``, optionally
wrapped in a ``Schedule`` for staleness tracking.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from mediavocab import (
    MediaType,
    PlaybackType,
    Release as MvRelease,
    StreamMode,
    Work,
)
from mediavocab.models.entity import EntityKind, EntityRef
from mediavocab.models.work import Programme, Schedule
from mediavocab.taxonomy import genre as _genre

from radiosoma import SomaFmStation, StreamVariant


# Audio-only provider axis. Importable by consumers that need to reason
# about the provider modality without instantiating a converter.
PLAYBACK_TYPE = {PlaybackType.AUDIO}


# Map SOMA's free-form ``<genre>`` tags to canonical
# ``mediavocab.taxonomy.genre.GENRE_*`` constants. SOMA tokens are
# separated by ``,`` and ``|``; tokens not present in this table fall
# through as raw lower-cased strings (per axiom 10.2 escape-hatch
# behaviour).
_GENRE_MAP = {
    "ambient": _genre.GENRE_AMBIENT,
    "downtempo": _genre.GENRE_AMBIENT,  # closest canonical match
    "chillout": _genre.GENRE_AMBIENT,
    "electronic": _genre.GENRE_ELECTRONIC,
    "electronica": _genre.GENRE_ELECTRONIC,
    "house": _genre.GENRE_HOUSE,
    "techno": _genre.GENRE_TECHNO,
    "trance": _genre.GENRE_TRANCE,
    "drum and bass": _genre.GENRE_DRUM_AND_BASS,
    "dnb": _genre.GENRE_DRUM_AND_BASS,
    "dubstep": _genre.GENRE_DUBSTEP,
    "indie": _genre.GENRE_INDIE,
    "alternative": _genre.GENRE_INDIE,
    "rock": _genre.GENRE_ROCK,
    "pop": _genre.GENRE_POP,
    "punk": _genre.GENRE_PUNK,
    "metal": _genre.GENRE_METAL,
    "jazz": _genre.GENRE_JAZZ,
    "blues": _genre.GENRE_BLUES,
    "soul": _genre.GENRE_SOUL,
    "funk": _genre.GENRE_FUNK,
    "rnb": _genre.GENRE_RNB,
    "r&b": _genre.GENRE_RNB,
    "reggae": _genre.GENRE_REGGAE,
    "country": _genre.GENRE_COUNTRY,
    "americana": _genre.GENRE_FOLK,
    "folk": _genre.GENRE_FOLK,
    "classical": _genre.GENRE_CLASSICAL,
    "hip hop": _genre.GENRE_HIP_HOP,
    "hip-hop": _genre.GENRE_HIP_HOP,
    "hiphop": _genre.GENRE_HIP_HOP,
    "rap": _genre.GENRE_HIP_HOP,
    "world": _genre.GENRE_LATIN,  # SOMA "world" tag is closest to latin/world music
    "latin": _genre.GENRE_LATIN,
    "disco": _genre.GENRE_DISCO,
    "comedy": _genre.GENRE_COMEDY,
    "news": "news",
    "talk": "talk_show",
    "spoken word": _genre.GENRE_SPOKEN_WORD,
    "drone": _genre.GENRE_AMBIENT,
    "experimental": _genre.GENRE_AMBIENT,
}


def _normalise_genres(raw) -> List[str]:
    """Tokenise SOMA's free-form genre string and resolve canonical
    constants where possible."""
    if not raw:
        return []
    if isinstance(raw, list):
        tokens = [str(g).strip().lower() for g in raw if g]
    else:
        # SOMA uses both "," and "|" as separators.
        tokens = []
        for sep in ("|", ","):
            raw = str(raw).replace(sep, "\n")
        for tok in str(raw).split("\n"):
            tok = tok.strip().lower()
            if tok:
                tokens.append(tok)
    out: List[str] = []
    seen = set()
    for tok in tokens:
        canonical = _GENRE_MAP.get(tok, tok)
        if canonical not in seen:
            seen.add(canonical)
            out.append(canonical)
    return out


def _epoch_to_iso(value) -> Optional[str]:
    """Validate a unix epoch (seconds, str or int) as an ISO datetime
    string with UTC offset, suitable for mediavocab's ``IsoDate`` type."""
    if value is None or value == "":
        return None
    try:
        ts = int(value)
    except (TypeError, ValueError):
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


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


def _station_work(station: SomaFmStation) -> Work:
    """Build the canonical ``Work`` for a SOMA channel."""
    extra: dict = {}
    if station.streams:
        extra["stream_urls"] = ",".join(station.streams)
    if station.description:
        extra["description"] = station.description
    if station.dj:
        extra["dj"] = station.dj
    if station.listeners is not None:
        extra["listeners"] = str(station.listeners)
    if station.last_playing:
        extra["last_playing"] = station.last_playing

    external_ids: dict = {}
    if station.station_id:
        external_ids["soma_fm_channel_id"] = str(station.station_id)

    return Work(
        title=station.title,
        media_type=MediaType.RADIO,
        broadcaster_country="US",
        language="en",
        # ``runtime`` is intentionally omitted (None): a continuous live
        # broadcast has no finite duration.
        content_genres=_normalise_genres(station.genre),
        external_ids=dict(external_ids),
        extra=extra,
    )


def _variant_to_release(
    work: Work,
    station: SomaFmStation,
    variant: StreamVariant,
) -> MvRelease:
    external_ids: dict = {}
    if station.station_id:
        external_ids["soma_fm_channel_id"] = str(station.station_id)
    extra: dict = {
        "soma_pls_source": variant.source,
    }
    if variant.format:
        extra["soma_format"] = variant.format
    return MvRelease(
        work=work,
        uri=variant.url,
        image=station.image or "",
        stream_mode=StreamMode.CONTINUOUS,
        codec=variant.codec,
        container=variant.container,
        bitrate=variant.bitrate,
        audio_channels="stereo",
        audio_language="en",
        external_ids=external_ids,
        extra=extra,
    )


def station_to_release(station: SomaFmStation) -> MvRelease:
    """Convert a :class:`SomaFmStation` to a single mediavocab
    :class:`Release` wrapping the highest-quality stream.

    For the full set of bitrate/codec variants use
    :func:`station_to_releases`.
    """
    work = _station_work(station)
    variants = station.stream_variants
    if not variants:
        # Build an empty release so callers always get a valid object.
        return MvRelease(
            work=work,
            uri="",
            image=station.image or "",
            stream_mode=StreamMode.CONTINUOUS,
            audio_channels="stereo",
            audio_language="en",
            external_ids={
                "soma_fm_channel_id": str(station.station_id)
            } if station.station_id else {},
        )
    return _variant_to_release(work, station, variants[0])


def station_to_releases(station: SomaFmStation) -> List[MvRelease]:
    """Return one :class:`Release` per stream variant.

    Per axiom 8 each distinct codec/bitrate encoding is a different
    ``Release`` of the same ``Work``; SOMA exposes 4 such variants
    per channel (high-quality AAC, MP3, low-bitrate HE-AAC, lo-fi
    HE-AAC). All releases share the same underlying ``Work`` instance
    so consumers can deduplicate by identity.
    """
    work = _station_work(station)
    return [_variant_to_release(work, station, v) for v in station.stream_variants]


def song_to_programme(
    song: dict,
    station: SomaFmStation,
) -> Optional[Programme]:
    """Convert a recent-tracks entry to a mediavocab :class:`Programme`.

    ``song`` is a raw dict scraped from ``https://somafm.com/songs/<id>.xml``
    with keys ``title``, ``artist``, ``album``, ``date`` (unix epoch as str).
    Returns ``None`` if the entry has no playable title.

    The programme's ``work`` is an :class:`EntityRef` describing the
    individual song; ``track_artist`` and ``track_album`` (when present)
    are mirrored into ``work.external_ids`` and ``programme.extra``.
    """
    title = (song.get("title") or "").strip()
    if not title:
        return None

    artist = (song.get("artist") or "").strip()
    album = (song.get("album") or "").strip()
    name = f"{artist} - {title}" if artist else title

    work_ext: dict = {}
    if artist:
        work_ext["track_artist"] = artist
    if album:
        work_ext["track_album"] = album

    track_extra: dict = {}
    if album:
        track_extra["album"] = album
    if artist:
        track_extra["artist"] = artist
    if song.get("albumart"):
        track_extra["albumart"] = song["albumart"]

    work_ref = Work(
        title=name,
        media_type=MediaType.MUSIC,
        external_ids=work_ext,
    )

    starts_at = _epoch_to_iso(song.get("date")) or datetime.now(
        tz=timezone.utc
    ).isoformat()

    channel_work = _station_work(station)

    return Programme(
        work=work_ref,
        channel=channel_work,
        starts_at=starts_at,
        is_live=True,
        is_repeat=False,
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


def recent_tracks_to_schedule(
    songs: list,
    station: SomaFmStation,
) -> Schedule:
    """Wrap the recent-tracks feed in a :class:`Schedule`.

    The SOMA recent-tracks feed is a rolling log of recently played
    songs; mediavocab models that as a ``Schedule`` with ``source =
    "somafm.com"`` and ``fetched_at`` set to the current wall clock.
    The first programme's ``starts_at`` becomes ``valid_from`` (oldest
    SOMA returns first in source order is the most recent track, so we
    take the min/max conservatively).
    """
    programmes = recent_tracks_to_programmes(songs, station)
    programmes = sorted(programmes, key=lambda p: p.starts_at or "")
    # Schedule requires non-tail programmes to have ends_at set; chain
    # each programme's ends_at to its successor's starts_at.
    for i in range(len(programmes) - 1):
        programmes[i] = programmes[i].model_copy(
            update={"ends_at": programmes[i + 1].starts_at}
        )
    starts = [p.starts_at for p in programmes if p.starts_at]
    valid_from = min(starts) if starts else None
    valid_until = max(starts) if starts else None
    return Schedule(
        channel=_station_work(station),
        programmes=programmes,
        source="somafm.com",
        fetched_at=datetime.now(tz=timezone.utc).isoformat(),
        valid_from=valid_from,
        valid_until=valid_until,
    )
