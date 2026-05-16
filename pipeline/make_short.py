#!/usr/bin/env python3
"""
9:16 short-form (~60s) built natively vertical from the "Connection"
movement: the campfire, the banjo-playing Hearthian, the dawn village.
Composed for vertical framing (not a center-crop of the wide cut).

QUALITY=draft -> 540x960 ultrafast ; QUALITY=final -> 1080x1920 hq
"""
import os, subprocess, sys, shlex

ROOT = "/home/user/playground"
RAW  = f"{ROOT}/raw/steam_reveal.mp4"
SEGS = f"{ROOT}/segs_v"
OUT  = f"{ROOT}/out"
Q    = os.environ.get("QUALITY", "draft")
if Q == "final":
    W, H, PRESET, CRF = 1080, 1920, "slow", "18"
else:
    W, H, PRESET, CRF = 540, 960, "ultrafast", "26"
FPS = 30
XF  = 1.0
os.makedirs(SEGS, exist_ok=True); os.makedirs(OUT, exist_ok=True)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2500:]); sys.exit(1)

GRADE = "eq=contrast=1.07:saturation=1.10:brightness=0.012:gamma=0.98,vignette=PI/4.5"

def fill_vert(extra=""):
    # cover 9:16 from a 16:9 source frame, subtle zoom for life
    return (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,"
            f"crop={W*2}:{H*2},{extra}scale={W}:{H},{GRADE},format=yuv420p")

def kb(idx, ts, dur, zexpr):
    out=f"{SEGS}/s_{idx:02d}.mp4"; png=f"{SEGS}/s_{idx:02d}.png"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",f"{ts}",
         "-i",RAW,"-vframes","1","-q:v","2",png])
    fr=int(dur*FPS)
    vf=(f"scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,"
        f"zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={fr}:s={W}x{H}:fps={FPS},{GRADE},format=yuv420p")
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1",
         "-t",f"{dur:.2f}","-i",png,"-vf",vf,"-r",str(FPS),
         "-c:v","libx264","-preset",PRESET,"-crf",CRF,"-pix_fmt","yuv420p",out])
    return out,dur

def mo(idx, ss, span, dur):
    out=f"{SEGS}/s_{idx:02d}.mp4"; fac=dur/span
    vf=f"setpts={fac:.3f}*PTS,"+fill_vert()
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",f"{ss}",
         "-t",f"{span}","-i",RAW,"-vf",vf,"-an","-r",str(FPS),
         "-c:v","libx264","-preset",PRESET,"-crf",CRF,"-pix_fmt","yuv420p",out])
    return out,dur

ZIN="min(zoom+0.0006,1.18)"; ZOUT="if(eq(on,1),1.18,max(zoom-0.0006,1.0))"
EDL=[
 ("kb",64.0,12.0,ZIN),    # dawn village
 ("kb",11.0,12.0,ZIN),    # campfire embers
 ("mo",9.0,3.0,9.0),      # campfire live slow-mo
 ("kb",18.5,13.0,ZIN),    # Hearthian playing banjo by fire
 ("kb",15.0,12.0,ZIN),    # marshmallow over the fire
 ("kb",11.0,11.0,ZOUT),   # embers, pull out — close
]

def main():
    files,durs=[],[]
    for i,it in enumerate(EDL):
        if it[0]=="kb": f,d=kb(i,it[1],it[2],it[3])
        else:           f,d=mo(i,it[1],it[2],it[3])
        files.append(f); durs.append(d); print("seg",i,it[0],d)
    n=len(durs); inp=[]
    for f in files: inp+=["-i",f]
    fc=[]; prev="0:v"; acc=durs[0]
    for i in range(1,n):
        off=acc-XF; lbl=f"x{i}"
        fc.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[{lbl}]")
        prev=lbl; acc=acc+durs[i]-XF
    fc.append(f"[{prev}]format=yuv420p[v]")
    out=f"{OUT}/owmv-shortform-9x16.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y"]+inp+
        ["-filter_complex",";".join(fc),"-map","[v]","-c:v","libx264",
         "-preset",PRESET,"-crf",CRF,"-pix_fmt","yuv420p","-r",str(FPS),out])
    d=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0",out],capture_output=True,text=True).stdout.strip()
    print(f"DONE -> {out} ({d}s)")

if __name__=="__main__": main()
