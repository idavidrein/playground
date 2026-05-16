# Outer Wilds × "Sit Around the Fire" — fan music video

A non-commercial fan tribute: a silent picture cut of *Outer Wilds* footage,
timed to the structure of **"Sit Around the Fire"** by Jon Hopkins, East
Forest & Ram Dass (8:22, *Music for Psychedelic Therapy*, 2021).

## What's here

- `out/owmv-final.mp4` — the finished **silent** picture cut (~8:25, 1920×1080)
- `out/owmv-shortform-9x16.mp4` — a ~60s vertical clip (the campfire / "Connection" section)
- `mux_audio.sh` — one-line script to lay the song under the picture
- `pipeline/make_video.py` — the full edit pipeline (reproducible)
- `PLAN.md` — the creative storyboard / movement map

## Why the song isn't included

The recording is copyrighted. It is **not** redistributed in this repo. To
finish the video, buy the track (Bandcamp: `jonhopkins.bandcamp.com`, ~$1.50,
goes to the artists) and run:

```bash
./mux_audio.sh ~/Music/sit-around-the-fire.flac
# -> out/owmv-final-with-music.mp4
```

The picture is built ~3s longer than the song; the mux uses the audio as the
master clock (`-shortest`) with a 2s fade-out, so the music is never clipped
and there is no black tail.

## The edit (why it moves)

The song's image *is* the game's image: a wise voice over people sitting
around a fire. The cut runs in five movements that track the track's arc —
sparse field-recording opening → spoken-word on presence → piano → chime
climax → instrumental tail:

| Movement | ~Time | Picture |
|---|---|---|
| I · Stillness | 0:00–1:00 | the campfire, embers, marshmallow |
| II · Wonder & solitude | 1:00–3:30 | the solar system, the Sun, lone exploration |
| III · Connection | 3:30–5:30 | the dawn village, a Hearthian playing banjo by the fire |
| IV · Awe & letting go | 5:30–7:30 | the green vortex, the anglerfish, the fire/lava peak |
| V · Becoming | 7:30–8:22 | back to the fire, embers, fade to dark |

Movement III is the emotional center and doubles as the short-form clip:
the lyric about not being able to be alone plays over the in-game travelers'
campfire — the exact image the song describes.

## Footage source & rights

All footage is from the **official Outer Wilds Reveal Trailer**, hosted
publicly by Mobius Digital via Steam. It is muted, recut, slowed and
re-graded — a transformative, non-commercial fan work. Mobius Digital is
permissive about non-commercial fan content. If you publish this, credit:

- Game & footage: **Outer Wilds** © Mobius Digital / Annapurna Interactive
- Music: **"Sit Around the Fire"** — Jon Hopkins, East Forest, Ram Dass
  (Domino Recording Co.)

Do not monetize. Keep it a tribute.

## Rebuild from scratch

```bash
QUALITY=final python3 pipeline/make_video.py     # ~10 min on 4 cores
./mux_audio.sh /path/to/song.flac
```
