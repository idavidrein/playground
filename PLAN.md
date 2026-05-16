# Outer Wilds × "Sit Around the Fire" — Music Video Plan

## Context

You want an inspiring fan video setting Outer Wilds gameplay to "Sit Around the Fire" by Jon Hopkins, East Forest, and Ram Dass (8:22, closing track of *Music for Psychedelic Therapy*, 2021). The pairing is unusually well-matched:

- The song's central image is *literally* people sitting around a fire while a wise voice speaks. Outer Wilds' core ritual — and its ending — is travelers sitting around campfires across the solar system, playing instruments together. Riebeck (banjo) at Brittle Hollow, Chert (drums) on Ember Twin, Esker (whistles) on the Moon, Gabbro (flute) on Giant's Deep, Feldspar (harmonica) in Dark Bramble, all converging at the Eye.
- Ram Dass's themes — presence, letting go, "you couldn't possibly be alone," "you already have it all" — map directly onto the game's emotional thesis: a 22-minute loop ending in a supernova, accepted with awe rather than dread, leading to a new universe.

Constraints driving this plan:
- I can't capture or edit video. **You** will source clips and edit. This plan is the storyboard, shot list, and timing map.
- You chose: existing YouTube footage (via yt-dlp), abstract/symbolic ending imagery (no narrative spoilers), 16:9 longform first with a flagged 60s segment for short-form.

## Deliverable shape

A single 8:22 cut at 1920×1080 16:9, audio = full track, video = stitched gameplay clips with crossfades. No on-screen text; let the spoken word and visuals carry it. One ~60s window (Movement III, see below) flagged as the short-form candidate.

## Execution mode

I am building this end-to-end myself: install tools, download audio + footage with yt-dlp, edit with ffmpeg, produce the final mp4. I will iterate until a watchable cut exists at `/home/user/playground/out/owmv-longform-1080p.mp4` and a 9:16 short at `/home/user/playground/out/owmv-shortform-9x16.mp4`. Fan/non-commercial tribute; credits in a sidecar README.

## Phase 1 — Source the audio

- Buy the track on Bandcamp (`jonhopkins.bandcamp.com/track/sit-around-the-fire`) — supports the artist and gets you a clean 24-bit WAV/FLAC. Don't rip from YouTube; it's lossy and ad-injected.
- Drop the file into your editor as the master timeline. **All shot timing is keyed to this file.**

## Phase 2 — Source the gameplay footage

Use `yt-dlp` to download segments from no-commentary playthroughs and from in-game cinematic compilations. Recommended source channels (search "Outer Wilds no commentary 4K"):

- **No-commentary full playthroughs**: search "Outer Wilds full game no commentary 4K" — pick a recording with HDR/high-bitrate, ideally a single long video so timestamps are stable.
- **Curated cinematic compilations**: search "Outer Wilds cinematic", "Outer Wilds beautiful moments", "Outer Wilds sunrise timelapse" — these tend to have the supernova, sand-pillar, Quantum Moon shots already isolated.
- **OST visual videos**: "Outer Wilds Travelers all instruments" — useful for the campfire imagery but be careful, many of these include the Ancient Glade reveal which is a narrative spoiler.

`yt-dlp` recipe (per clip):

```bash
# Best video+audio merged, then trim to the segment you need
yt-dlp -f "bv*[height<=2160]+ba/b" --merge-output-format mp4 "<URL>" -o "raw/%(id)s.%(ext)s"
ffmpeg -ss <start> -to <end> -i raw/<id>.mp4 -c copy clips/<scene>.mp4
```

Mobius Digital is famously permissive about fan content — but your video is still derivative. Add a description crediting Mobius Digital, Jon Hopkins, East Forest, and the Ram Dass estate, mark it non-commercial, and don't monetize.

## Phase 3 — Editor

DaVinci Resolve (free) is the right tool: handles 4K, has good crossfades, free color grading. CapCut also works for a faster path. Avoid iMovie — it'll fight you on the long crossfades this edit needs.

## Phase 4 — Movement-by-movement shot list

Song structure (approximate — verify against the actual file in your editor):
- **0:00 – ~3:30**: Field recordings, sparse lo-fi pulses, first Ram Dass passage on presence/being.
- **~3:30 – ~5:30**: Piano enters; "you don't need loneliness… you don't need greed… you don't need doubt" passage.
- **~5:30 – ~7:30**: Chimes layer in; spoken word climax on love and the source.
- **~7:30 – 8:22**: Instrumental tail; voice fades.

The five movements below match those four sections plus a quiet opening and a final exhale.

### Movement I — Stillness (~0:00 – ~1:00)
*Field recordings, near-silence. Establish the world.*

- 0:00 — Black. Hold 3 seconds.
- 0:03 — Slow fade up: the Hearthian protagonist sitting at the campfire near the launchpad on Timber Hearth, looking up. **This is the visual rhyme with the song title — make it the first image.**
- 0:20 — Cut to: stargazer kid (Hornfels area) looking up through the observatory.
- 0:35 — Wide pan of the Timber Hearth night sky, the other planets visible.
- 0:50 — First-person POV: closing eyes / wake-up moment (the loop's restart, used here as "arrival" not as "death").

### Movement II — Wonder & solitude (~1:00 – ~3:30)
*Sparse beats begin. Ram Dass starts speaking. Lone exploration; the universe is vast and the protagonist is small.*

- 1:00 — Launch from Timber Hearth, ship climbing through atmosphere.
- 1:20 — Drifting in space, planets in frame, no UI if possible.
- 1:40 — Landing on Brittle Hollow, lava reflections.
- 2:00 — Walking alone on Ember Twin's surface as sand falls from sky.
- 2:20 — Standing at the edge of Giant's Deep, ocean stretching to horizon.
- 2:40 — Floating in Dark Bramble fog, anglerfish silhouettes (use sparingly — keep the awe, not the threat).
- 3:00 — A held shot of the protagonist sitting alone on a cliff watching the binary system.
- 3:20 — Push toward the Sun, light blooming.

**Pacing note**: longer holds here (5–8s per shot). The song is sparse; the cuts should breathe with it.

### Movement III — Connection (~3:30 – ~5:30) ⭐ short-form candidate
*Piano enters. "You don't need loneliness…" begins. Travelers' campfires.*

This is the most literal lyric-to-image mapping in the whole edit and the strongest 60s for a short-form cut.

- 3:30 — Hard cut on piano entrance: **first traveler campfire**. Riebeck on Brittle Hollow, banjo across knees, fire crackling. Time the cut precisely to the first piano note.
- 3:50 — Chert on Ember Twin's pole, drums, stars wheeling overhead.
- 4:10 — Esker on the Lunar Outpost, whistling, Earth-analog (Timber Hearth) hanging in the sky.
- 4:30 — Gabbro in their hammock on Giant's Deep, flute, clouds.
- 4:50 — Feldspar in Dark Bramble, harmonica, deep in the fog.
- 5:10 — Cross-cut quickly between all five fires as the music thickens — 1–2s per shot, building.

**This 3:30–4:30 window (60s) is your short-form clip**: each campfire one shot, lyric anchoring is "you couldn't possibly be alone," instruments mirror Ram Dass's words about love. Reframe to 9:16 by centering on character + fire and cropping wider environment.

### Movement IV — Awe & letting go (~5:30 – ~7:30)
*Chimes layer in. Spoken word climax. Cosmic scale, time, surrender.*

- 5:30 — Sand columns on Ash Twin / Ember Twin, a continuous shot of sand falling from one world to the other (the visual metaphor for time draining).
- 5:50 — Time-loop sunrise: dawn breaking on Timber Hearth, fast cut.
- 6:05 — Wide shot of the Quantum Moon, vanishing and reappearing as the camera looks away (let the quantum effect sell "you already know" without text).
- 6:25 — Sun Station: the protagonist standing on the platform as the Sun fills the frame.
- 6:45 — **Supernova**. Hold this shot. The Sun goes red giant, then collapses, then the white wave races outward. This is the song's highest point and the game's most awe-inducing image. Time the white-light wave's arrival to the loudest chime swell.
- 7:10 — White frame. Hold 3–4 seconds. Audio carries alone.

### Movement V — Becoming (~7:30 – 8:22)
*Spoken word ends. Instrumental tail. Symbolic ending — abstract enough not to spoil.*

Per your spoiler choice: show fire, instruments, hands, marshmallows, light — **not** the Ancient Glade environment, **not** the recognizable observatory geometry, **not** the new-universe planet reveal.

- 7:30 — Extreme close-ups, no environment context: flames flickering, a banjo string vibrating, a marshmallow on a stick, a Hearthian face lit orange by firelight, hands resting near the fire.
- 7:55 — Pull back slowly, but stop before the wider gathering composition reads as "the ending."
- 8:05 — Slow dissolve to a single wide shot of stars or a nebula — feels like "after," doesn't spoil "what."
- 8:15 — Fade to black with the audio tail.
- 8:22 — End. No credits card on the cut itself; put credits in the YouTube description.

## Phase 5 — Editing notes

- **Crossfades, not hard cuts**, except on the piano entrance at 3:30 and the supernova white-flash at ~6:45. Those two moments are where the image should *snap* with the music.
- **Color**: lift Outer Wilds' already-warm palette slightly. The game has strong oranges (campfires, Ember Twin, the Sun) and deep blacks (space). Don't over-grade — the source already looks great.
- **Audio ducking**: do NOT add foley or ambient game audio. The track is the only audio. Mute every clip's audio track on import.
- **Aspect**: master in 16:9 1080p or 2160p. For the short-form, re-export the 3:30–4:30 segment with a 9:16 crop, centered on character.
- **Watch for**: HUD elements in source footage. Many no-commentary playthroughs still show the suit UI, signalscope, etc. Prefer clips where the player toggled HUD off, or crop/cover with a vignette.

## Critical files / assets

- `audio/sit-around-the-fire.flac` — the master audio
- `raw/` — full-length yt-dlp downloads (don't delete; you'll re-trim)
- `clips/` — trimmed segments named by movement (e.g. `m3-riebeck.mp4`, `m4-supernova.mp4`)
- `project.drp` (or equivalent) — your editor project
- `out/owmv-longform-1080p.mp4` and `out/owmv-shortform-9x16.mp4`

## Verification

End-to-end test once a rough cut exists:

1. **Sync check**: scrub to 3:30. The first piano note must land within 100ms of the cut to Riebeck's campfire. If it drifts, the rest of the edit drifts.
2. **Supernova sync**: at ~6:45, the white shockwave's leading edge must hit the loudest chime swell. This is the emotional peak; if it's off, redo just this cut.
3. **No-spoiler check**: have someone who hasn't played Outer Wilds watch Movement V (7:30–8:22) only. Ask: "what do you think happens next?" If they describe the actual ending mechanic, you've shown too much — pull tighter close-ups.
4. **Mobile check**: watch the longform on a phone with phone speakers. The spoken word must remain intelligible — it carries the meaning. If the music is overpowering Ram Dass at any point, you've got a clip with bleed-through audio.
5. **Short-form check**: re-export Movement III standalone. It must work without the longform context — the 5 traveler shots should read as "found family / not alone" on their own.

## Open considerations (call out, don't block)

- The 8:22 runtime exceeds many viewers' attention; consider a 30-second teaser as a third deliverable (last 8 seconds of Movement IV + first 22 seconds of Movement V).
- If the abstract ending feels too coy in practice, the symbolic option allows showing the campfire gathering as silhouettes only — discuss after rough cut if it lands flat.
