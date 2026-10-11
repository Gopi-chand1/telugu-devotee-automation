#!/usr/bin/env python3
"""Turn a production manifest into a per-scene Google Flow prompt pack.

Input: output/production_manifest.csv (or --manifest PATH)
Output: output/flow_prompt_pack/scene_01/IMAGE_PROMPT.txt, MOTION_PROMPT.txt,
DIALOGUE_TELUGU.txt, LIP_SYNC.txt, plus a review index and ZIP.
No image/video/audio generation or publishing is performed.
"""
import argparse
import csv
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def clean_dialogue(value):
    return re.sub(r"^\s*\[PARAPHRASE\]\s*", "", value or "", flags=re.I).strip()


def safe_text(value):
    return (value or "").strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="output/production_manifest.csv")
    parser.add_argument("--output-dir", default="output/flow_prompt_pack")
    args = parser.parse_args()

    manifest = (ROOT / args.manifest).resolve()
    out_dir = (ROOT / args.output_dir).resolve()
    if not manifest.is_file():
        raise SystemExit(f"ERROR: production manifest not found: {manifest}")

    with manifest.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit("ERROR: manifest has no scene rows.")

    rows.sort(key=lambda row: int(row["scene_number"]))
    if len({int(row["scene_number"]) for row in rows}) != len(rows):
        raise SystemExit("ERROR: duplicate scene numbers found in manifest.")

    if out_dir.exists():
        for path in sorted(out_dir.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        out_dir.rmdir()
    out_dir.mkdir(parents=True, exist_ok=True)

    index = []
    for row in rows:
        number = int(row["scene_number"])
        folder = out_dir / f"scene_{number:02d}"
        folder.mkdir(parents=True)
        fields = {
            "IMAGE_PROMPT.txt": row.get("image_prompt", ""),
            "MOTION_PROMPT.txt": row.get("motion_prompt", ""),
            "DIALOGUE_TELUGU.txt": clean_dialogue(row.get("dialogue_telugu", "")),
            "LIP_SYNC.txt": row.get("lip_sync", ""),
        }
        missing = [name for name, value in fields.items() if not (value or "").strip()]
        for filename, value in fields.items():
            (folder / filename).write_text(safe_text(value), encoding="utf-8")
        scene_meta = {
            "scene_number": number,
            "speaker": row.get("speaker", ""),
            "place": row.get("place", ""),
            "review_status": row.get("review_status", "NEEDS_REVIEW"),
            "missing_fields": missing,
            "note": "Review before generation. This pack contains prompts only.",
        }
        (folder / "SCENE_INFO.json").write_text(
            json.dumps(scene_meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        index.append(scene_meta)

    (out_dir / "README_TELUGU.md").write_text(
        "# TELUGU DEVOTEE — Scene Prompt Pack\n\n"
        f"Scenes included: {len(rows)}.\n\n"
        "Each scene folder contains image prompt, motion prompt, Telugu dialogue, and lip-sync notes.\n"
        "The [PARAPHRASE] marker is removed from dialogue files. No video/audio was generated.\n"
        "Check each scene and character continuity before using prompts. Keep the current review status; "
        "do not treat NEEDS_REVIEW as approved.\n",
        encoding="utf-8",
    )
    (out_dir / "scene_index.json").write_text(
        json.dumps({"project": "TELUGU DEVOTEE", "scene_count": len(rows), "scenes": index},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    zip_path = out_dir.parent / "telugu-devotee-flow-prompt-pack.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(out_dir.parent))
    print(f"Prepared {len(rows)} scene folders: {out_dir}")
    print(f"ZIP: {zip_path}")
    print("Prompts only — no video generation, audio generation, or publishing.")
    if any(item["missing_fields"] for item in index):
        print("WARNING: one or more scenes have missing fields; inspect scene_index.json.")


if __name__ == "__main__":
    main()
