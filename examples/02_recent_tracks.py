"""02 — Fetch and print the recent-tracks feed for a channel."""
import sys
from radiosoma import get_recent_tracks

channel_id = sys.argv[1] if len(sys.argv) > 1 else "groovesalad"

songs = get_recent_tracks(channel_id)
print(f"Recent tracks for '{channel_id}' ({len(songs)} entries):\n")

for song in songs[:10]:
    artist = song.get("artist", "")
    title = song.get("title", "")
    album = song.get("album", "")
    date = song.get("date", "")
    print(f"  {date}  {artist} - {title}  [{album}]")
