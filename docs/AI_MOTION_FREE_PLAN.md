# TELUGU DEVOTEE — Free AI Motion Video Plan

## Current verified state

- `.github/workflows/daily.yml` generates `output/episode_package.md` (scene prompts and SEO) and uploads it as a GitHub Actions artifact.
- The standard `ubuntu-latest` GitHub-hosted runner used by this workflow is not a guaranteed GPU runtime. Do not run a diffusion video model on it and assume it will work.
- The linked `Gopi-chand1/AutoTube` project currently generates one AI image and loops that image with FFmpeg. That is image-to-video packaging, not genuine generated character motion.
- AutoTube's existing `generate-video.yml` can upload directly to YouTube. Do not connect it to the daily workflow unchanged because this project requires review before publication.

## Free/open model candidate

**Wan2.1 T2V-1.3B** is an open video-generation model. Its official project says the 1.3B model can generate short 480p clips and cites about 8.19 GB VRAM as its minimum GPU memory requirement. This makes it a plausible test on a free notebook GPU when one is available, but it does not guarantee that a free Colab GPU will be assigned or remain available.

Official model and instructions: https://github.com/Wan-Video/Wan2.1

## Honest cost and capacity limits

- Model weights and source code can be downloaded without paying for the model, subject to their license.
- A GPU is still required for practical generation. Free notebook GPU access is variable, sessions can disconnect, and storage/time quotas apply.
- Generating 60 separate clips for a 10-minute episode is not guaranteed to finish in one free session. Start with one 5-second test clip, then process small batches and save each batch to persistent storage.
- Avoid hosted video APIs unless their current free quota and terms are verified. Do not assume that an API is unlimited or permanently free.
- Gemini script generation remains a separate dependency and requires the existing `GEMINI_API_KEY` GitHub secret.

## Required safe workflow

1. Generate the episode script with the existing `daily.yml` workflow.
2. Run an open-model motion test outside the CPU-only GitHub runner (for example, a free notebook GPU session when available).
3. Generate clips in small batches; preserve each scene's prompt and character reference notes.
4. Stitch completed clips and Telugu audio with FFmpeg, then upload the result as a **review artifact**.
5. Do not call the YouTube upload API and do not set any video to public automatically.
6. Only after a human approves the rendered video should a separate, explicitly triggered upload workflow be used.

## Why the AI motion stage is not enabled in GitHub Actions yet

The current repository has no verified, always-available free GPU runner. Enabling a model download and inference step on the existing CPU runner would likely fail, run out of memory, or waste Actions minutes. A genuinely free end-to-end motion pipeline needs either a compatible local GPU or a temporary free GPU notebook, with the latter not being reliably schedulable every day.
