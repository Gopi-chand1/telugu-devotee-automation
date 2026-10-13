# TELUGU DEVOTEE — Free GPU Motion Test Setup

## Safety and cost rules
- This route is experimental; Kaggle GPU availability and quota are not guaranteed.
- Do not add a paid API or billing-enabled service.
- Do not add YouTube upload/publishing steps. Generated video must remain a review artifact.
- Never paste Kaggle credentials into chat, source files, workflow YAML, or notebook output.

## One-time account setup (Android browser)
1. Open https://www.kaggle.com/settings and sign in.
2. In the API section, create a new API token. Keep the downloaded token private.
3. Open the repository https://github.com/Gopi-chand1/telugu-devotee-automation/settings/secrets/actions
4. Add repository Actions secrets only if/when a reviewed workflow is ready to use them:
   - `KAGGLE_USERNAME`: the username shown in your Kaggle profile.
   - `KAGGLE_KEY`: the private API key from Kaggle.
5. Never commit `kaggle.json`, the API key, or any token into the repository.

## Before running a GPU job
- Confirm the intended notebook uses a Kaggle-supported accelerator and that your account can access it.
- Start with one scene only; do not submit all 60 scenes on the first run.
- Check the model's current license, model download size, Kaggle GPU quota, session limits, and internet access from the notebook environment.
- Keep the output private and review the clip manually for character consistency, visual quality, and Telugu lip-sync. The existing Wan2.1 smoke-test notebook creates a short silent motion test, not a complete 10-second scene with voice or lip-sync.

## Current status
This document does not run a notebook or create a video. It records the credential boundary and safe setup requirements. A Kaggle-based job still needs an implementation and a one-scene validation run before it can be called working. No YouTube publishing is configured here.
