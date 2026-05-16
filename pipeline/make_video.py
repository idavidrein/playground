#!/usr/bin/env python3
"""
Outer Wilds x "Sit Around the Fire" — silent picture cut.
Renders per-segment clips (Ken Burns stills + slow-mo motion) then crossfades
them into one timed video. Audio is added separately via mux_audio.sh so no
copyrighted recording is reproduced in this repo.

QUALITY=draft  -> 960x540 ultrafast (fast iteration)
QUALITY=final  -> 1920x1080 high quality
"""
import os, subprocess, math, sys, shlex

ROOT = "/home/user/playground"
RAW  = f"{ROOT}/raw/steam_reveal.mp4"          # official Steam-hosted OW reveal trailer
SEGS = f"{ROOT}/segs"
OUT  = f"{ROOT}/out"
Q    = os.environ.get("QUALITY", "draft")

if Q == "final":
    W, H, PRESET, CRF, FPS = 1920, 1080, "medium", "19", 30
else:
    W, H, PRESET, CRF, FPS = 960, 540, "ultrafast", "26", 30

XF = 1.2          # crossfade seconds between segments
TARGET = 505.0    # total video seconds (song ~502s; mux uses -shortest)

os.makedirs(SEGS, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED:", " ".join(shlex.quote(c) for c in cmd[:8]), "...")
        print(r.stderr[-3000:])
        sys.exit(1)
    return r

# Gentle, warm grade shared by every segment. Keeps OW's palette, adds glow.
GRADE = ("eq=contrast=1.07:saturation=1.10:brightness=0.012:gamma=0.98,"
         "vignette=PI/4.5")

# Pre-upscale still ONCE to this size (enough headroom for 1.16x zoom,
# NOT applied per-frame). ~1.4x output, even dims.
PREW = (int(W * 1.4) // 2) * 2
PREH = (int(H * 1.4) // 2) * 2

def kb_filter(move, dur):
    """Ken Burns on an already-upscaled still (no per-frame scale)."""
    frames = int(round(dur * FPS))
    z_in  = "min(zoom+0.00045,1.16)"
    z_out = "if(eq(on,1),1.16,max(zoom-0.00045,1.0))"
    cx = "iw/2-(iw/zoom/2)"
    cy = "ih/2-(ih/zoom/2)"
    if move == "in":      z, x, y = z_in,  cx, cy
    elif move == "out":   z, x, y = z_out, cx, cy
    elif move == "in_l":  z, x, y = z_in,  f"(iw-iw/zoom)*(on/{frames})", cy
    elif move == "in_r":  z, x, y = z_in,  f"(iw-iw/zoom)*(1-on/{frames})", cy
    elif move == "in_up": z, x, y = z_in,  cx, f"(ih-ih/zoom)*(1-on/{frames})"
    elif move == "in_dn": z, x, y = z_in,  cx, f"(ih-ih/zoom)*(on/{frames})"
    else:                 z, x, y = z_in,  cx, cy
    return (f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},"
            f"{GRADE},format=yuv420p")

def render_kb(idx, ts, move, dur):
    out = f"{SEGS}/seg_{idx:03d}.mp4"
    still = f"{SEGS}/still_{idx:03d}.png"
    frames = int(round(dur * FPS))
    # extract + upscale ONCE
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",f"{ts}",
         "-i",RAW,"-vframes","1","-vf",
         f"scale={PREW}:{PREH}:flags=lanczos","-q:v","2",still])
    # feed exactly ONE image; zoompan emits `frames`; -frames:v caps output
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",still,
         "-vf",kb_filter(move,dur),"-frames:v",str(frames),
         "-r",str(FPS),"-c:v","libx264","-preset",PRESET,"-crf",CRF,
         "-threads","4","-an","-pix_fmt","yuv420p",out])
    return out, dur

def render_motion(idx, ss, span, dur, zoom=1.0, yshift=0.0):
    """Slow-mo: take `span`s of source from `ss`, stretch to `dur`s."""
    out = f"{SEGS}/seg_{idx:03d}.mp4"
    factor = dur / span                       # >1 = slower
    crop = ""
    if zoom > 1.0:
        crop = (f"crop=iw/{zoom}:ih/{zoom}:"
                f"(iw-iw/{zoom})/2:(ih-ih/{zoom})/2+{yshift}*ih,")
    vf = (f"{crop}setpts={factor:.4f}*PTS,"
          f"scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},{GRADE},format=yuv420p")
    run(["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-ss",f"{ss}","-t",f"{span}","-i",RAW,
         "-vf",vf,"-an","-r",str(FPS),
         "-c:v","libx264","-preset",PRESET,"-crf",CRF,
         "-pix_fmt","yuv420p",out])
    return out, dur

# ---------------------------------------------------------------------------
# EDL  (kind, args, dur, move/zoom)   durations are pre-crossfade
#   kb : Ken Burns on still at timestamp T
#   mo : slow motion of source [ss, ss+span]
# Safe source ranges in reveal trailer: 7-55s and 62-77s
#   (text overlay ~55-62s, OW logo 77s+, ESRB 0-7s — all avoided)
# ---------------------------------------------------------------------------
EDL = [
 # ---- I. STILLNESS (the fire) ----
 ("kb", 8.0,  "in",   7.0),    # dark trees, almost black — opens from nothing
 ("kb", 11.0, "in",   20.0),   # campfire embers — hero, slow push in
 ("mo", 9.0, 3.0,     17.0),   # campfire live, deep slow-mo
 ("kb", 11.0, "out",  18.0),   # campfire, pull back (different framing)
 ("kb", 15.0, "in_up",18.0),   # campfire + marshmallow, rise
 # ---- II. WONDER & SOLITUDE (cosmos / scale) ----
 ("kb", 42.5, "in",   22.0),   # the solar system — hero cosmic
 ("mo", 41.0, 3.5,    16.0),   # solar system drift, slow-mo
 ("kb", 45.5, "in_r", 18.0),   # ship silhouette vs the Sun
 ("kb", 49.5, "in_l", 18.0),   # astronaut shadow on bright surface
 ("mo", 47.5, 3.0,    14.0),   # surface walk slow-mo
 ("kb", 24.0, "in",   18.0),   # Giant's Deep green canyon + tornado
 ("mo", 23.0, 4.0,    16.0),   # canyon/tornado slow-mo
 ("kb", 29.0, "in_up",16.0),   # pink tornado + lone figure
 ("kb", 52.0, "in",   15.0),   # bright cavern / blue glyph structure
 # ---- III. CONNECTION (warmth, others, the song) ----
 ("kb", 64.0, "in",   20.0),   # village at dawn (Timber Hearth) — hero warm
 ("kb", 18.5, "in",   22.0),   # Hearthian playing banjo by fire — the traveler
 ("mo", 18.0, 3.0,    13.0),   # banjo/character live, slow-mo
 ("kb", 15.0, "in_dn",20.0),   # campfire + marshmallow, intimate
 ("kb", 11.0, "in_l", 18.0),   # campfire embers — return, new framing
 ("kb", 64.0, "out",  15.0),   # village — pull out, breathe
 # ---- IV. AWE & LETTING GO (the sublime, surrender) ----
 ("kb", 34.0, "in",   18.0),   # green vortex-eye — hypnotic, "letting go"
 ("mo", 30.5, 4.0,    18.0),   # spout ascent into the vortex, slow-mo
 ("kb", 65.5, "in",   16.0),   # anglerfish silhouette in fog — the sublime
 ("mo", 63.0, 3.0,    9.0),    # anglerfish / dark drift slow-mo
 ("kb", 45.5, "in_l", 14.0),   # Sun + ship — return, scale
 ("mo", 72.0, 3.5,    13.0),   # lava flight slow-mo
 ("kb", 75.5, "in",   18.0),   # astronaut against fiery lava sun — climax
 ("kb", 73.0, "in_up",16.0),   # astronaut bathed in fire glow — peak
 # ---- V. BECOMING (return to the fire, release) ----
 ("kb", 15.0, "out",  18.0),   # marshmallow campfire — return
 ("kb", 18.5, "out",  15.0),   # banjo Hearthian — return
 ("kb", 11.0, "in",   20.0),   # campfire embers — final, very slow
 ("kb", 8.0,  "in",   10.0),   # back to dark trees — fade toward nothing
]

def main():
    print(f"[{Q}] rendering {len(EDL)} segments at {W}x{H} ...")
    seg_files, durs = [], []
    for i, item in enumerate(EDL):
        if item[0] == "kb":
            _, ts, move, dur = item
            f, d = render_kb(i, ts, move, dur)
        else:
            _, ss, span, dur = item
            f, d = render_motion(i, ss, span, dur)
        seg_files.append(f); durs.append(d)
        print(f"  seg {i:02d} {item[0]} dur={d:.1f}s")

    # Crossfade chain. total = sum(d) - (n-1)*XF . Scale to TARGET via last seg.
    n = len(durs)
    base_total = sum(durs) - (n - 1) * XF
    # adjust final segment so total == TARGET
    adj = TARGET - base_total
    durs[-1] += adj
    # re-render last seg at its new duration
    last = EDL[-1]
    if last[0] == "kb":
        render_kb(n-1, last[1], last[2], durs[-1])
    print(f"adjusted final seg by {adj:+.1f}s -> total {TARGET:.1f}s")

    # Build single-pass xfade filtergraph
    inputs = []
    for f in seg_files:
        inputs += ["-i", f]
    fc = []
    prev = "0:v"
    acc = durs[0]
    for i in range(1, n):
        off = acc - XF
        lbl = f"x{i}"
        fc.append(f"[{prev}][{i}:v]xfade=transition=fade:"
                  f"duration={XF}:offset={off:.3f}[{lbl}]")
        prev = lbl
        acc = acc + durs[i] - XF
    # gentle emergence from / return to black (song is master at ~502s)
    fade_out_st = TARGET - 6.0
    fc.append(f"[{prev}]fade=t=in:st=0:d=3.0,"
              f"fade=t=out:st={fade_out_st:.1f}:d=4.0,"
              f"format=yuv420p[v]")
    filt = ";".join(fc)

    out = f"{OUT}/owmv-{'final' if Q=='final' else 'draft'}.mp4"
    cmd = ["ffmpeg","-hide_banner","-loglevel","error","-y"] + inputs + [
        "-filter_complex", filt, "-map","[v]",
        "-c:v","libx264","-preset",PRESET,"-crf",CRF,
        "-pix_fmt","yuv420p","-r",str(FPS), out]
    print("compositing crossfade chain ...")
    run(cmd)
    d = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0",out],capture_output=True,text=True).stdout.strip()
    print(f"DONE -> {out}  ({d}s)")

if __name__ == "__main__":
    main()
