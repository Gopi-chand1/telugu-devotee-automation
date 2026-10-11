# Assemble the TELUGU DEVOTEE review MP4

This local helper joins scene clips in numeric order and places the matching Telugu voice track on each clip. It does not generate video, create Telugu audio, or upload/publish to YouTube.

## Requirements
- Python 3 (standard library only for this script)
- FFmpeg and FFprobe installed and available on PATH
- The production manifest CSV
- A video clip and Telugu voice track for every scene

## Folder layout
```
output/production_manifest.csv
assets/flow-clips/S01_flow_v1.mp4
assets/voices/S01_voice_v1.wav
...
```

The filenames in the manifest columns `flow_clip_filename` and `voice_filename` are used. Scene clips and voice tracks must be named accordingly, or the manifest must be updated to match the actual files.

## Approval gate
The script intentionally stops unless every scene's `review_status` is `APPROVED` or `READY`. The current manifest may still say `NEEDS_REVIEW`; do not mark scenes approved until you have checked their prompts, generated assets, and Telugu dialogue.

## Run
From the repository root:

```bash
python scripts/assemble_review_video.py
```

Optional background music (use music you have permission to use):

```bash
python scripts/assemble_review_video.py --music assets/music/approved_music.mp3 --music-volume 0.06
```

Default output: `output/telugu_devotee_review.mp4`. Each scene is trimmed/padded to 10 seconds, so the 30-scene episode will be about 5 minutes. The Telugu voice file is used as the scene audio; this does not create or guarantee character lip-sync. Watch the full exported video before publishing.

## Current limitation
This helper assembles existing files only. Google Flow clips and Telugu voice tracks still need to be generated/exported by a supported tool, and those external web interfaces are not controlled by this script. No publishing action is performed.
