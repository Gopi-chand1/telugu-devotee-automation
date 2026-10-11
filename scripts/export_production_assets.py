#!/usr/bin/env python3
"""Export reviewed TELUGU DEVOTEE scene prompts into a production handoff manifest.

Reads output/episode_package.md and writes:
  output/production_manifest.json
  output/production_manifest.csv

No API calls, credentials, video generation, or publishing are performed.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "output" / "episode_package.md"
OUT_DIR = ROOT / "output"

SCENE_RE = re.compile(
    r"^###\s+SCENE\s+(\d+)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
FIELD_RE = re.compile(
    r"^\s*(IMAGE PROMPT|MOTION PROMPT|DIALOGUE|LIP-SYNC)\s*:\s*(.*)$",
    re.MULTILINE | re.IGNORECASE,
)


def parse_scene_block(block):
    fields = {}
    matches = list(FIELD_RE.finditer(block))
    for i, match in enumerate(matches):
        key = match.group(1).upper()
        start = match.end()
        # Keep any same-line text after the label, then include the section body
        # up to the next recognized field.
        end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
        value = (match.group(2) + block[start:end]).strip()
        fields[key] = re.sub(r"\n{3,}", "\n\n", value)
    return fields


def main():
    if not SOURCE.exists():
        raise SystemExit(
            f"ERROR: {SOURCE} not found. Generate or download the episode package first."
        )
    text = SOURCE.read_text(encoding="utf-8")
    matches = list(SCENE_RE.finditer(text))
    if not matches:
        raise SystemExit(
            "ERROR: no '### SCENE N | Speaker | Place' headings found. "
            "Check the script package format."
        )

    scenes = []
    seen = set()
    for i, match in enumerate(matches):
        number = int(match.group(1))
        if number in seen:
            print(f"WARNING: duplicate scene number {number}; keeping the first.", file=sys.stderr)
            continue
        seen.add(number)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[match.end():end].strip()
        fields = parse_scene_block(block)
        scene = {
            "scene_number": number,
            "speaker": match.group(2).strip(),
            "place": match.group(3).strip(),
            "image_prompt": fields.get("IMAGE PROMPT", ""),
            "motion_prompt": fields.get("MOTION PROMPT", ""),
            "dialogue_telugu": fields.get("DIALOGUE", ""),
            "lip_sync": fields.get("LIP-SYNC", ""),
            "review_status": "NEEDS_REVIEW",
            "flow_clip_filename": f"S{number:02d}_flow_v1.mp4",
            "voice_filename": f"S{number:02d}_voice_v1.wav",
        }
        missing = [
            key for key in ("image_prompt", "motion_prompt", "dialogue_telugu", "lip_sync")
            if not scene[key]
        ]
        if missing:
            scene["parse_warning"] = "Missing fields: " + ", ".join(missing)
            print(f"WARNING: scene {number} missing {', '.join(missing)}", file=sys.stderr)
        scenes.append(scene)

    scenes.sort(key=lambda item: item["scene_number"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "production_manifest.json"
    csv_path = OUT_DIR / "production_manifest.csv"

    json_path.write_text(
        json.dumps(
            {
                "project": "TELUGU DEVOTEE",
                "source": str(SOURCE.relative_to(ROOT)),
                "scene_count": len(scenes),
                "note": "Review prompts before use. This manifest does not generate or publish video.",
                "scenes": scenes,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    columns = [
        "scene_number", "speaker", "place", "image_prompt", "motion_prompt",
        "dialogue_telugu", "lip_sync", "review_status", "flow_clip_filename",
        "voice_filename", "parse_warning",
    ]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(scenes)

    print(f"Exported {len(scenes)} scenes:")
    print(f"  {json_path.relative_to(ROOT)}")
    print(f"  {csv_path.relative_to(ROOT)}")
    print("Review all prompts and dialogue before using them in video tools.")


if __name__ == "__main__":
    main()
