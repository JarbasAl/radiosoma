"""04 — Convert a channel to a mediavocab Release and inspect its shape."""
from radiosoma import get_stations
from radiosoma.converters import MODALITY, station_to_release

station = next(s for s in get_stations() if s.station_id == "groovesalad")
release = station_to_release(station)

# Work (the channel itself)
work = release.work
print("Work")
print(f"  title:          {work.title}")
print(f"  media_type:     {work.media_type}")
print(f"  country:        {work.country}")
print(f"  language:       {work.language}")
print(f"  runtime:        {work.runtime}  # None = continuous live broadcast")
print(f"  content_genres: {work.content_genres}")
print(f"  external_ids:   {work.external_ids}")
print()

# Release (a specific stream encoding)
print("Release")
print(f"  uri:            {release.uri}")
print(f"  stream_mode:    {release.stream_mode}")
print(f"  codec:          {release.codec}")
print(f"  container:      {release.container}")
print(f"  bitrate:        {release.bitrate} kbps")
print(f"  audio_channels: {release.audio_channels}")
print(f"  audio_language: {release.audio_language}")
print(f"  image:          {release.image}")
print(f"  external_ids:   {release.external_ids}")
print()

# Provider modality axis
print(f"MODALITY: {MODALITY}")
