#!/usr/bin/env bash
# Add the music to the finished silent picture cut.
#
# This repo ships ONLY the silent video. The song "Sit Around the Fire"
# (Jon Hopkins, East Forest, Ram Dass) is copyrighted and is intentionally
# NOT redistributed here. Supply your own legitimately-obtained file
# (Bandcamp purchase: jonhopkins.bandcamp.com — ~1 minute, supports the artist).
#
# Usage:
#   ./mux_audio.sh /path/to/sit-around-the-fire.flac
#   ./mux_audio.sh /path/to/song.mp3 out/owmv-final.mp4
#
set -euo pipefail

AUDIO="${1:?Usage: ./mux_audio.sh <audio-file> [video-file]}"
VIDEO="${2:-out/owmv-final.mp4}"
OUTDIR="out"
BASE="$(basename "${VIDEO%.*}")"
FINAL="${OUTDIR}/${BASE}-with-music.mp4"

[ -f "$AUDIO" ] || { echo "audio not found: $AUDIO" >&2; exit 1; }
[ -f "$VIDEO" ] || { echo "video not found: $VIDEO (run build first)" >&2; exit 1; }

# -shortest: the audio is the master clock; video is built ~3s long so the
# music never gets clipped and there is no black tail. A gentle 2s audio
# fade-out is added so the end lands softly.
ALEN=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO")
FADE_START=$(awk "BEGIN{print ($ALEN>2)?$ALEN-2:0}")

ffmpeg -hide_banner -loglevel error -y \
  -i "$VIDEO" -i "$AUDIO" \
  -filter_complex "[1:a]afade=t=out:st=${FADE_START}:d=2[a]" \
  -map 0:v -map "[a]" \
  -c:v copy -c:a aac -b:a 256k \
  -shortest "$FINAL"

echo "wrote $FINAL"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL" \
  | awk '{printf "duration: %.1fs\n",$1}'
