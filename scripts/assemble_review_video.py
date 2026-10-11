#!/usr/bin/env python3
"""Assemble reviewed TELUGU DEVOTEE scene clips and Telugu voice tracks.

Expected inputs:
  output/production_manifest.csv
  assets/flow-clips/S01_flow_v1.mp4 ... (or filenames in the CSV)
  assets/voices/S01_voice_v1.wav ... (or filenames in the CSV)

This tool does not generate clips or voices. It creates a review MP4 from files
that already exist. Requires ffmpeg and ffprobe installed on the machine running it.
"""
import argparse
import csv
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(command):
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(map(str, command))}\n"
            f"{result.stderr[-3000:]}"
        )


def duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"ffprobe could not read {path}: {result.stderr}")
    return float(result.stdout.strip())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="output/production_manifest.csv")
    parser.add_argument("--clips", default="assets/flow-clips")
    parser.add_argument("--voices", default="assets/voices")
    parser.add_argument("--output", default="output/telugu_devotee_review.mp4")
    parser.add_argument("--seconds", type=float, default=10.0)
    parser.add_argument("--music", default="", help="Optional background music file")
    parser.add_argument("--music-volume", type=float, default=0.08)
    args = parser.parse_args()

    for binary in ("ffmpeg", "ffprobe"):
        if not shutil.which(binary):
            raise SystemExit(f"ERROR: {binary} is required but was not found in PATH.")

    manifest = (ROOT / args.manifest).resolve()
    clips_dir = (ROOT / args.clips).resolve()
    voices_dir = (ROOT / args.voices).resolve()
    output = (ROOT / args.output).resolve()
    music = (ROOT / args.music).resolve() if args.music else None

    if not manifest.is_file():
        raise SystemExit(f"ERROR: manifest not found: {manifest}")
    if music and not music.is_file():
        raise SystemExit(f"ERROR: music file not found: {music}")

    with manifest.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows.sort(key=lambda row: int(row["scene_number"]))
    if not rows:
        raise SystemExit("ERROR: manifest has no scenes.")

    required = []
    for row in rows:
        n = int(row["scene_number"])
        if row.get("review_status", "").strip().upper() not in {"APPROVED", "READY"}:
            raise SystemExit(
                f"ERROR: scene {n} is not approved (review_status="
                f"{row.get('review_status', '')!r}). Review the manifest first."
            )
        clip_name = (row.get("flow_clip_filename") or f"S{n:02d}_flow_v1.mp4").strip()
        voice_name = (row.get("voice_filename") or f"S{n:02d}_voice_v1.wav").strip()
        clip = clips_dir / clip_name
        voice = voices_dir / voice_name
        if not clip.is_file():
            required.append(f"scene {n}: missing clip {clip}")
        if not voice.is_file():
            required.append(f"scene {n}: missing Telugu voice track {voice}")
    if required:
        raise SystemExit("ERROR: required files are missing:\n- " + "\n- ".join(required))

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="telugu-devotee-") as temp:
        temp_dir = Path(temp)
        segments = []
        for row in rows:
            n = int(row["scene_number"])
            clip = clips_dir / row["flow_clip_filename"].strip()
            voice = voices_dir / row["voice_filename"].strip()
            segment = temp_dir / f"scene_{n:04d}.mp4"
            # Keep the clip's video, replace its audio with the Telugu dialogue,
            # pad short dialogue with silence, and enforce the target scene length.
            run([
                "ffmpeg", "-y", "-v", "error",
                "-i", str(clip), "-i", str(voice),
                "-filter_complex",
                f"[0:v]trim=duration={args.seconds},setpts=PTS-STARTPTS[v];"
                f"[1:a]aresample=48000,apad,atrim=duration={args.seconds},"
                "asetpts=PTS-STARTPTS[a]",
                "-map", "[v]", "-map", "[a]",
                "-t", str(args.seconds), "-c:v", "libx264", "-preset", "veryfast",
                "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-movflags", "+faststart", str(segment),
            ])
            segments.append(segment)

        concat_list = temp_dir / "concat.txt"
        concat_list.write_text(
            "".join("file '" + str(p).replace("'", "'\\''") + "'\n" for p in segments),
            encoding="utf-8",
        )
        if music:
            run([
                "ffmpeg", "-y", "-v", "error",
                "-f", "concat", "-safe", "0", "-i", str(concat_list),
                "-stream_loop", "-1", "-i", str(music),
                "-filter_complex",
                f"[1:a]volume={args.music_volume},atrim=duration={len(rows)*args.seconds},"
                f"asetpts=PTS-STARTPTS[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=2[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output),
            ])
        else:
            run([
                "ffmpeg", "-y", "-v", "error",
                "-f", "concat", "-safe", "0", "-i", str(concat_list),
                "-c", "copy", "-movflags", "+faststart", str(output),
            ])

    print(f"Created review video: {output}")
    print(f"Scenes: {len(rows)} | Target duration: {len(rows) * args.seconds:.1f} seconds")
    print("Watch the full video and approve it before publishing.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
