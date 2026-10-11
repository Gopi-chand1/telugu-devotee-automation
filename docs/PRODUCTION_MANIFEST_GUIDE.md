# Export scene prompts for Flow / Vids / Canva

The episode generator currently creates `output/episode_package.md`. The production exporter converts its scene sections into JSON and CSV files so you can track each scene and copy the correct prompts/dialogue into the video tools.

## Run locally

From the repository root:

```bash
python3 scripts/export_production_assets.py
```

It writes:
- `output/production_manifest.json` — structured scene records, including image prompt, motion prompt, Telugu dialogue, lip-sync notes, review status, and suggested clip filenames.
- `output/production_manifest.csv` — spreadsheet-friendly version for scene tracking.

## Run in Google Colab

1. Download or upload the repository files into a Colab session.
2. Ensure `output/episode_package.md` exists in the repository folder.
3. Run `python3 scripts/export_production_assets.py`.
4. Download `output/production_manifest.csv` and open it in a spreadsheet.
5. Review the scene's image prompt, motion prompt, Telugu dialogue, and lip-sync notes before pasting them into Flow/Vids.

## Important

- This exporter only parses an existing Markdown script. It does not call Google Flow, Google Vids, or Canva APIs.
- It does not generate video, voiceover, VFX, or upload anything to YouTube.
- Scenes with missing parsed fields are flagged in the output and must be corrected manually.
- A `NEEDS_REVIEW` status is intentional; do not mark scenes approved until you have watched them with audio.
- Do not commit large video files, credentials, cookies, or API keys to GitHub.
