# TELUGU DEVOTEE — Ramayanam Video Automation

This repository generates a 60-scene episode script package and SEO metadata. The daily GitHub Actions workflow currently produces a Markdown artifact; it does **not** yet generate a complete video or publish to YouTube.

## Existing workflow

- Workflow: [`.github/workflows/daily.yml`](.github/workflows/daily.yml)
- Script skill: [`skills/yt-script/SKILL.md`](skills/yt-script/SKILL.md)
- SEO skill: [`skills/yt-seo/SKILL.md`](skills/yt-seo/SKILL.md)
- Motion plan and free-tier limits: [`docs/AI_MOTION_FREE_PLAN.md`](docs/AI_MOTION_FREE_PLAN.md)

## Test real AI motion (manual review; no YouTube upload)

Open the [Wan2.1 Colab motion test notebook](https://colab.research.google.com/github/Gopi-chand1/telugu-devotee-automation/blob/main/notebooks/wan21_free_motion_test.ipynb). It attempts to generate one very short silent test clip using the open Wan2.1 T2V 1.3B model. A free GPU session is not guaranteed; the first model download is large and can fail due to storage, RAM/VRAM, or session limits.

**Safety gate:** The notebook has no YouTube upload step. Generated clips must be reviewed manually. Do not add upload credentials or enable public publishing unless the owner explicitly approves the final video.

## Cost and limitations

- GitHub Actions can generate the Markdown script package, subject to the configured Gemini API quota and GitHub usage limits.
- Wan2.1 model weights are open source, but running inference still requires suitable compute. Free hosted GPU availability and runtime duration vary.
- The test notebook produces silent video only; it does not yet add Telugu voice, lip-sync, music, or assemble all 60 scenes into a long episode.
