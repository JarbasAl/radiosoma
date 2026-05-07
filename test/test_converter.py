"""Offline unit tests for ``radiosoma.converters``."""
from __future__ import annotations

from mediavocab import MediaType, PlaybackModality, StreamMode

from radiosoma import SomaFmStation
from radiosoma.converters import (
    MODALITY,
    recent_tracks_to_programmes,
    song_to_programme,
    station_to_release,
)


def _station(**overrides):
    raw = dict(
        id="groovesalad",
        title="Groove Salad",
        description="A nicely chilled plate of ambient/downtempo beats and grooves.",
        genre="ambient,downtempo",
        xlimage="https://somafm.com/img/groovesalad-large.jpg",
        highestpls=[{"text": "https://ice.somafm.com/groovesalad-256-mp3"}],
        fastpls=[{"text": "https://ice.somafm.com/groovesalad-128-mp3"}],
    )
    raw.update(overrides)
    return SomaFmStation(raw)


def test_modality_is_audio_only():
    assert MODALITY == {PlaybackModality.AUDIO}


def test_to_release_uses_radio_media_type():
    rel = station_to_release(_station())
    assert rel.work.media_type == MediaType.RADIO


def test_to_release_uses_continuous_stream_mode():
    rel = station_to_release(_station())
    assert rel.stream_mode == StreamMode.CONTINUOUS


def test_to_release_uri_prefers_best_stream():
    rel = station_to_release(_station())
    assert rel.uri == "https://ice.somafm.com/groovesalad-256-mp3"


def test_to_release_carries_image():
    rel = station_to_release(_station())
    assert rel.image == "https://somafm.com/img/groovesalad-large.jpg"


def test_to_release_external_ids_use_soma_fm_channel_id():
    rel = station_to_release(_station())
    assert rel.work.external_ids.get("soma_fm_channel_id") == "groovesalad"
    # Same id mirrored on the Release for convenience.
    assert rel.external_ids.get("soma_fm_channel_id") == "groovesalad"


def test_to_release_channel_id_is_string_typed():
    rel = station_to_release(_station(id=12345))
    assert rel.work.external_ids["soma_fm_channel_id"] == "12345"
    assert isinstance(rel.work.external_ids["soma_fm_channel_id"], str)


def test_to_release_country_and_language_are_us_english():
    rel = station_to_release(_station())
    assert rel.work.country == "US"
    assert rel.work.language == "en"


def test_to_release_genre_split_into_content_genres():
    rel = station_to_release(_station(genre="ambient,downtempo,chillout"))
    assert "ambient" in rel.work.content_genres
    assert "downtempo" in rel.work.content_genres
    assert "chillout" in rel.work.content_genres


def test_to_release_genre_list_passed_through():
    rel = station_to_release(_station(genre=["Ambient", "Downtempo"]))
    assert rel.work.content_genres == ["ambient", "downtempo"]


def test_to_release_handles_missing_optional_fields():
    bare = SomaFmStation({"id": "secretagent", "title": "Secret Agent"})
    rel = station_to_release(bare)
    assert rel.work.title == "Secret Agent"
    assert rel.work.media_type == MediaType.RADIO
    assert rel.work.content_genres == []
    assert rel.uri == ""


def test_song_to_programme_basic():
    station = _station()
    song = {
        "title": "Luminis",
        "artist": "Luis Junior",
        "album": "Urban Woman .01",
        "date": "1778114640",
    }
    prog = song_to_programme(song, station)
    assert prog is not None
    assert prog.work.name == "Luis Junior - Luminis"
    assert prog.channel.external_ids["soma_fm_channel_id"] == "groovesalad"
    assert prog.is_live is True
    assert prog.extra["album"] == "Urban Woman .01"
    assert prog.extra["artist"] == "Luis Junior"
    # IsoDate validator accepts ISO datetimes with offset.
    assert prog.starts_at.startswith("20")


def test_song_to_programme_skips_empty_title():
    assert song_to_programme({"title": "", "date": "1778114640"}, _station()) is None


def test_recent_tracks_to_programmes_filters_empty():
    station = _station()
    songs = [
        {"title": "A", "artist": "X", "date": "1778114640"},
        {"title": "", "artist": "", "date": "1778114000"},
        {"title": "B", "artist": "Y", "date": "1778113000"},
    ]
    progs = recent_tracks_to_programmes(songs, station)
    assert len(progs) == 2
    assert progs[0].work.name == "X - A"
    assert progs[1].work.name == "Y - B"
