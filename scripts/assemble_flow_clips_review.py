#!/usr/bin/env python3
"""Build a review-only MP4 from numbered video clips and optional separate Telugu voice WAVs."""
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

def numbered_files(root, suffixes):
    found = []
    if root and Path(root).exists():
        for p in Path(root).rglob("*"):
            if p.is_file() and p.suffix.lower() in suffixes:
                n = scene_number(p)
                if n is not None:
                    found.append((n, p))
    found.sort(key=lambda x: x[0])
    nums = [n for n, _ in found]
    if len(nums) != len(set(nums)):
        raise SystemExit(f"ERROR: Duplicate numbered files found in {root}. Keep one file per scene.")
    return dict(found)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", default="incoming-clips")
    ap.add_argument("--audio-dir", default=None, help="Optional directory of per-scene WAVs (S01.wav or scene_001.wav). These replace clip audio.")
    ap.add_argument("--output", default="output/telugu_devotee_review.mp4")
    ap.add_argument("--seconds", type=float, default=10.0)
    args = ap.parse_args()
    if args.seconds <= 0:
        raise SystemExit("ERROR: --seconds must be greater than zero.")
    for binary in ("ffmpeg", "ffprobe"):
        if not shutil.which(binary):
            raise SystemExit(f"ERROR: {binary} is required.")
    clips = numbered_files(args.clips, {".mp4"})
    if not clips:
        raise SystemExit("ERROR: No numbered MP4 clips found. Name files S01.mp4, S02.mp4 ...")
    audios = numbered_files(args.audio_dir, {".wav", ".mp3", ".m4a", ".aac", ".flac"}) if args.audio_dir else {}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="td-review-") as td:
        td = Path(td)
        segments = []
        for n, clip in clips.items():
            seg = td / f"scene_{n:04d}.mp4"
            voice = audios.get(n)
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "a:0",
                 "-show_entries", "stream=index", "-of", "csv=p=0", str(clip)],
                text=True, capture_output=True)
            has_clip_audio = probe.returncode == 0 and bool(probe.stdout.strip())
            cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(clip)]
            if voice:
                cmd += ["-i", str(voice), "-map", "0:v:0", "-map", "1:a:0",
                        "-af", f"aresample=48000,apad,atrim=duration={args.seconds}",
                        "-c:a", "aac", "-b:a", "192k"]
            elif has_clip_audio:
                cmd += ["-map", "0:v:0", "-map", "0:a:0?",
                        "-af", f"aresample=48000,apad,atrim=duration={args.seconds}",
                        "-c:a", "aac", "-b:a", "160k"]
            else:
                cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                        "-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac", "-b:a", "160k"]
            vf = f"scale=trunc(iw/2)*2:trunc(ih/2)*2,fps=24,tpad=stop_mode=clone:stop_duration={args.seconds}"
            cmd += ["-vf", vf, "-t", str(args.seconds), "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
                    "-ar", "48000", "-movflags", "+faststart", str(seg)]
            run(cmd)
            segments.append(seg)
        concat = td / "concat.txt"
        concat.write_text("".join("file '" + str(p).replace("'", "'\\''") + "'\n" for p in segments), encoding="utf-8")
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
             "-i", str(concat), "-c", "copy", "-movflags", "+faststart", str(out)])
    matched = sum(1 for n in clips if n in audios)
    missing = sorted(set(clips) - set(audios)) if args.audio_dir else []
    print(f"Created review-only video: {out} ({len(clips)} scenes; {matched} separate voice tracks; not published)")
    if missing:
        print("WARNING: No separate voice WAV found for scenes: " + ", ".join(map(str, missing)) + ". Clip audio/silence was used.")

if __name__ == "__main__":
    main()
