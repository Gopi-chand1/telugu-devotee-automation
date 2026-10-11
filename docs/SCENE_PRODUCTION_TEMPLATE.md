# TELUGU DEVOTEE — Reusable Scene Production Template

Use this template after reviewing a scene in `output/episode_package.md`. Generate and approve one scene first; do not batch all 60 scenes until the test is acceptable.

## 1. Google Flow — image-to-video prompt

Paste the scene's existing IMAGE PROMPT into the image/reference workflow, then use this motion prompt. Replace bracketed values with the scene's actual content.

**Motion prompt**

> Create one 10-second cinematic shot for TELUGU DEVOTEE's Telugu Ramayanam. Scene: [SCENE NUMBER — PLACE — ACTION]. Use the supplied approved reference image as the identity and costume source. Preserve the same face, age, hairstyle, clothing, ornaments, body proportions, weapons, and art direction. Follow the scene's supplied MOTION PROMPT exactly: 0–3 seconds [opening action/camera], 3–6 seconds [continuing action/environment], 6–10 seconds [conclusion/transition]. Realistic cinematic Indian epic fantasy, grounded movement, natural cloth and hair motion, controlled atmospheric particles, believable light, stable anatomy, no modern objects, no subtitles, no logos, no watermark. Keep movement readable and do not introduce new characters or actions that are not in the script.

**Suggested generation settings:** use 16:9 landscape for the long YouTube episode where available. Choose the shortest clip duration that covers the actual shot; if the service cannot generate 10 seconds in one pass, create compatible shorter clips and join them in the editor. Keep the exported filename as `S01_flow_v1.mp4`, changing the scene number for each scene.

## 2. Telugu voiceover — Google Vids or another available voice tool

Use only the exact Telugu dialogue from the reviewed script. Do not translate it into English or add an invented narrator.

**Voice direction**

> Language: Telugu (India). Delivery: devotional, natural, emotionally controlled, clear pronunciation. Speaker: [CHARACTER NAME]. Emotion: [SCENE-APPROPRIATE EMOTION]. Pace the supplied line to fit the selected shot; preserve every Telugu word and name. Do not add greetings, explanations, or extra sentences. Leave a short silent tail at the end for the visual transition.

**Dialogue to record:** [COPY THE EXACT DIALOGUE FIELD FROM THE SCENE]

Check pronunciation of names, Telugu syllables, and the final timing by listening to the exported track. A generated voice track alone does not guarantee visual lip-sync. If the scene requires visible speaking, use a tool that explicitly supports talking-character lip-sync and manually verify the result; otherwise frame the speaker from a distance, from behind, or use a non-speaking shot rather than showing visibly mismatched lips.

## 3. Canva — edit card

For each approved scene, use one clip or a small group of shots that tell the same action. Keep visual continuity between scenes.

- **Timeline label:** `S01` (change per scene)
- **Video:** `S01_flow_v1.mp4`
- **Voice:** `S01_voice_v1.wav` or the exported voice format
- **Sound effects:** only scene-appropriate ambience/action; do not overpower dialogue
- **Music:** devotional cinematic instrumental with usage rights confirmed; keep it lower than dialogue
- **Subtitles:** exact Telugu dialogue, large enough for mobile screens, safe margins, checked spelling
- **Transition:** motivated cut, gentle dissolve, or brief sound bridge; avoid effects on every cut
- **Approval:** review image continuity, motion artifacts, dialogue timing, captions, sound levels, and rights before marking approved

## 4. File naming and approval

Use predictable names:
- `S01_still_v1.png`
- `S01_flow_v1.mp4`
- `S01_voice_v1.wav`
- `S01_canva_review_v1.mp4`

Mark a scene **APPROVED** only after watching it with audio. If it fails, keep the original and create `v2`; do not silently replace a good version.

## 5. First-scene acceptance checklist

- [ ] Character identity, costume, age, and props match the character locks.
- [ ] The visual action matches the script; no extra event is invented.
- [ ] Camera motion is stable and the subject is anatomically plausible.
- [ ] Telugu dialogue is exact and pronunciation is understandable.
- [ ] If visible speech is used, lip movement has been checked separately.
- [ ] Voice remains clear over music and sound effects.
- [ ] Telugu captions are correct and readable on a phone.
- [ ] Export plays correctly from beginning to end.
- [ ] No unlicensed music, watermarks, or accidental modern objects.
- [ ] Owner has reviewed the scene.

## Limitations

This is a reusable production worksheet, not an API integration. It does not sign into Google Flow, Google Vids, or Canva, and it does not automatically transfer files between them. Their features and free usage allowances can vary by account and region. Keep YouTube publishing manual until the final video has been reviewed and explicitly approved.
