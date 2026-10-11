# TELUGU DEVOTEE — Video Production Pipeline

This guide adds Google Flow, Google Vids, and Canva to the existing episode workflow. It does **not** change `.github/workflows/daily.yml` or trigger a workflow.

## Pipeline

1. **GitHub Actions** — generate the 60-scene script package and SEO draft. Review `output/episode_package.md` before production.
2. **Google Flow** — create cinematic scene clips from each scene's IMAGE PROMPT / MOTION PROMPT. Reuse the same approved character reference images for Rama, Lakshmana, Vishwamitra, Sita, and other recurring characters. Keep aspect ratio and visual style consistent. Save/export the selected clips locally or to Drive.
3. **Google Vids** — assemble clips in scene order and create Telugu voiceover from each scene's DIALOGUE where the voiceover feature is available. Confirm Telugu is selected and listen for pronunciation before using it. Add ambience/SFX only where appropriate. Do not assume generated voiceover is character lip-sync; it is a narration/voice track unless a supported talking-video workflow explicitly creates synced speech.
4. **Canva** — create a 16:9 YouTube video project, import the approved Flow/Vids clips, arrange them in scene order, add transitions, subtle VFX overlays, Telugu titles/subtitles, background music, and channel branding. Keep music below dialogue. Export an MP4 and watch the full video once.
5. **Human review** — check story accuracy, character continuity, Telugu pronunciation, sound levels, visual artifacts, music rights, and the final runtime. Publish to YouTube only after the owner approves.

## Suggested folder structure

- `assets/characters/` — approved character reference stills
- `assets/scene-stills/` — scene keyframes
- `assets/flow-clips/` — selected Google Flow exports
- `assets/vids-assembly/` — Google Vids drafts/exports
- `assets/canva-final/` — reviewed final MP4 and thumbnail

These are suggested locations; create them only if useful. Do not commit large generated videos to GitHub.

## Scene production checklist

For each scene:
- Match the script's scene number.
- Use the scene-specific image and motion prompts.
- Preserve faces, costume, weapons, age, and visual style from approved reference images.
- Check that the clip's action matches the next scene's continuity.
- Add the scene's Telugu dialogue/voice track and verify timing.
- Keep captions readable on a phone screen.
- Mark a scene as approved before using it in the final edit.

## Important automation and free-tier limits

- The current GitHub workflow is manual-only and should remain unchanged unless explicitly requested.
- This repository currently generates a Markdown script package. It does not itself sign in to Google Flow, Google Vids, or Canva, create clips in their web UIs, or publish a video.
- Google Flow, Google Vids, and Canva have separate account, region, feature, and usage limits. Confirm the options visible in your own account before planning a daily 60-scene output.
- For a practical first test, produce **one scene** in Flow, add/check a Telugu voiceover in Vids, import it into Canva, and export a short review MP4. Only scale up after this works reliably.
- Do not store API keys, passwords, or session cookies in this repository.
