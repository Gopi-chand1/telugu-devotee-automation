---
name: yt-script
description: Scene format and rules for TELUGU DEVOTEE Ramayanam episodes (10-second scenes, Telugu dialogue, image + motion prompts, lip-sync).
---

# yt-script / TELUGU DEVOTEE - Ramayanam mode

## Content rules
- Source: Valmiki Ramayanam only. Never invent events, speeches or facts. Mark any paraphrase [PARAPHRASE] and any doubt [VERIFY sarga].
- No narrator. Character-to-character Telugu dialogue only, in natural spoken Telugu.
- ONE speaker per scene. Dialogue is at most about 20 words.
- Every scene is exactly 10 seconds.
- Hook = scenes 1-2: a tense moment from the text, not a summary.
- Last scene of the episode: a story-relevant cliffhanger.

## Format of every scene (use exactly this header)

### SCENE <number> | <speaker> | <place>
IMAGE PROMPT: English. Must include the relevant CHARACTER LOCK text and the STYLE LOCK text (see locks.md) every time, plus action, environment, lighting, camera, composition and mood.
MOTION PROMPT:
- 0-3s: opening action and camera movement
- 3-6s: continuing action and environmental motion
- 6-10s: concluding action and transition
DIALOGUE: Telugu script, spoken by the named speaker.
LIP-SYNC: speech start to end time, which words land in which time window, and a mouth-closed tail. Only the speaker moves their mouth; all other characters keep their mouths closed.

## Continuity
- Faces, ages, costumes, proportions, props and weapons stay identical to the CHARACTER LOCK in every scene.
- Describe any new character in full the first time they appear and reuse that exact description afterwards.
- Runtime = number of scenes x 10 seconds.
