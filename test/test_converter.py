"""Offline unit test for ``radiosoma.converters.station_to_release``."""
from __future__ import annotations

from mediavocab import MediaType, StreamMode

from radiosoma import SomaFmStation
from radiosoma.converters import station_to_release


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


def test_to_release_external_ids_carry_somafm_id():
    rel = station_to_release(_station())
    assert rel.work.external_ids.get("somafm_id") == "groovesalad"


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
