# MoneyPrinterTurbo integration — TELUGU DEVOTEE

This integration is deliberately isolated on the `setup/moneyprinterturbo-video` branch. It does not edit the existing episode generator or daily workflow, and it never uploads to YouTube.

## What this setup does

1. Reuses a Markdown script already in this repository (default: `output/episode_package.md`).
2. Extracts Telugu dialogue/prose and submits one video task to a running MoneyPrinterTurbo API.
3. Waits for the task to finish and downloads the MP4 as a GitHub Actions artifact for human review.
4. Does not automatically publish anything.

## Important limitation

MoneyPrinterTurbo is primarily an automated short-video/stock-footage editor. This integration does **not** promise 60 scene-specific cinematic shots, consistent Ramayanam characters, character-to-character lip-sync, or advanced VFX. Stock footage may not depict the actual Ramayana scene. Inspect the output before using it. For dialogue-led scenes, use clean, labelled Telugu dialogue lines; one TTS voice is used for the initial test.

## One-time setup

### A. Run MoneyPrinterTurbo somewhere reachable

The GitHub Actions runner cannot use a server running only on your Android phone. Start MoneyPrinterTurbo on a trusted computer/server or use the upstream Google Colab notebook for a temporary test:

- Repository: https://github.com/harry0703/MoneyPrinterTurbo
- Colab notebook: https://colab.research.google.com/github/harry0703/MoneyPrinterTurbo/blob/main/docs/MoneyPrinterTurbo.ipynb
- API docs when the server is running: `https://YOUR-MPT-HOST/docs`

A Colab session is temporary; its URL may change and GitHub Actions must be run while the API endpoint is reachable. Do not expose an unauthenticated API publicly.

### B. Configure MoneyPrinterTurbo

In its private `config.toml`, set a strong `[app]` `api_key` value and configure a footage source. For Pexels footage, add a Pexels API key in the MoneyPrinterTurbo configuration/WebUI. Keep all keys private. Pexels/other footage providers have their own terms and quotas.

The current workflow requests `video_source=pexels`, Telugu language, Telugu Shruti voice, subtitles, one output video, and a 16:9 landscape aspect by default.

### C. Add GitHub Actions secrets

In this repository open **Settings → Secrets and variables → Actions → New repository secret** and add:

- `MPT_API_URL`: the base URL of the running MoneyPrinterTurbo server, e.g. `https://your-host.example` (do not append `/api/v1`).
- `MPT_API_KEY`: exactly the same key configured as `app.api_key` in MoneyPrinterTurbo.

Use HTTPS for any publicly reachable endpoint. Do not put secrets into the workflow file, script, or a public issue.

## Run a test

1. Open the Actions tab in this repository.
2. Select **TELUGU DEVOTEE - MoneyPrinterTurbo Video**.
3. Choose **Run workflow**.
4. Start with a short, clean Telugu script. If using the episode package, make sure it contains Telugu dialogue lines labelled `Dialogue:` or `డైలాగ్:`, or plain Telugu prose outside image/motion prompt sections.
5. After completion, open the `telugu-devotee-video-review` artifact and inspect the MP4.

The workflow is manual only, has no YouTube credentials or publishing step, and stores artifacts for 7 days.

## Troubleshooting

- **Missing MPT_API_URL**: add the Actions secret; the upstream API must be running and reachable from GitHub Actions.
- **401/403**: confirm `MPT_API_KEY` matches the server's `app.api_key`.
- **404**: confirm the base URL points to the MoneyPrinterTurbo API server and that `/api/v1/videos` exists in `/docs`.
- **Pexels/material errors**: configure a valid provider key and check provider quota/terms.
- **No Telugu text extracted**: use a clean Telugu script or label dialogue lines clearly in the Markdown.
- **Video generation failure**: inspect MoneyPrinterTurbo logs and the API task error. Paid AI video sources are not used by this workflow.

## Review checklist

- [ ] Story facts and sequence match the approved script.
- [ ] Telugu pronunciation, voice, and subtitles are correct.
- [ ] Footage is relevant, licensed, and not misleading.
- [ ] No unwanted English narration, artifacts, or visual errors.
- [ ] Approve manually before uploading to YouTube.
