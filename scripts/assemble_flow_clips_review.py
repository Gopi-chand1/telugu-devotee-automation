#!/usr/bin/env python3
"""Build a review-only MP4 from numbered Google Flow clips, preserving their audio."""
import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

def run(cmd):
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-2500:] or f"Command failed: {cmd}")

def scene_number(path):
    m = re.search(r"(?:scene|s)[ _-]*0*(\d+)", path.stem, re.I)
    return int(m.group(1)) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", default="incoming-clips")
    ap.add_argument("--output", default="output/telugu_devotee_review.mp4")
    ap.add_argument("--seconds", type=float, default=8.0)
    args = ap.parse_args()
    for binary in ("ffmpeg", "ffprobe"):
        if not shutil.which(binary):
            raise SystemExit(f"ERROR: {binary} is required.")
    root = Path(args.clips)
    clips = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() == ".mp4":
            n = scene_number(p)
            if n is not None:
                clips.append((n, p))
    clips.sort(key=lambda x: x[0])
    if not clips:
        raise SystemExit("ERROR: No numbered MP4 clips found. Name files S01.mp4, S02.mp4 ...")
    nums = [n for n, _ in clips]
    if len(nums) != len(set(nums)):
        raise SystemExit("ERROR: Duplicate scene numbers found. Keep one clip per scene.")
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="td-review-") as td:
        td = Path(td)
        segments = []
        for n, clip in clips:
            seg = td / f"scene_{n:04d}.mp4"
            # Preserve source audio if present; otherwise produce a silent video segment.
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "a:0",
                 "-show_entries", "stream=index", "-of", "csv=p=0", str(clip)],
                text=True, capture_output=True)
            has_audio = probe.returncode == 0 and bool(probe.stdout.strip())
            cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(clip),
                   "-t", str(args.seconds), "-map", "0:v:0"]
            if has_audio:
                cmd += ["-map", "0:a:0?", "-af", "aresample=48000,apad,atrim=duration=" + str(args.seconds),
                        "-c:a", "aac", "-b:a", "160k"]
            else:
                cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                        "-map", "1:a:0", "-shortest", "-c:a", "aac", "-b:a", "160k"]
            cmd += ["-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,fps=24",
                    "-t", str(args.seconds), "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "22", "-pix_fmt", "yuv420p", "-ar", "48000",
                    "-movflags", "+faststart", str(seg)]
            run(cmd)
            segments.append(seg)
        concat = td / "concat.txt"
        concat.write_text("".join("file '" + str(p).replace("'", "'\\''") + "'\n" for p in segments), encoding="utf-8")
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
             "-i", str(concat), "-c", "copy", "-movflags", "+faststart", str(out)])
    print(f"Created review-only video: {out} ({len(clips)} scenes; not published)")
if __name__ == "__main__":
    main()
