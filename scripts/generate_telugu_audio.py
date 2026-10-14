#!/usr/bin/env python3
"""Generate per-scene Telugu audio from output/episode_package.md using Indic Parler-TTS.

Designed for a GitHub Actions CPU runner. Saves each WAV immediately so a rerun
can resume without regenerating completed scenes. Does not publish to YouTube.
"""
import os
import re
import gc
import csv
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from huggingface_hub import HfApi
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = Path(os.environ.get("EPISODE_MARKDOWN", ROOT / "output/episode_package.md"))
OUT_DIR = Path(os.environ.get("AUDIO_OUTPUT_DIR", ROOT / "output/audio"))
MODEL_ID = "ai4bharat/indic-parler-tts"
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
VOICE_DESCRIPTION = (
    "A woman speaks in Telugu with a warm, clear, calm and devotional voice. "
    "She speaks at a moderate, natural pace with expressive pronunciation. "
    "The recording is clean and has no background noise."
)

def extract_scenes(markdown):
    """Read dialogue lines from both the current and legacy episode Markdown formats."""
    parts = re.split(r"(?m)^### Scene\s+(\d+)\s*[—-].*$", markdown)
    scenes = []
    dialogue_pattern = re.compile(
        r"(?m)^(?:DIALOGUE|Telugu Character Dialogue):\s*(.+?)\s*$"
    )
    for i in range(1, len(parts), 2):
        number, block = int(parts[i]), parts[i + 1]
        match = dialogue_pattern.search(block)
        if not match:
            continue
        line = match.group(1).strip()
        # Remove editorial labels; they are not spoken dialogue.
        line = re.sub(r"^\[(?:PARAPHRASE|VERIFY[^\]]*)\]\s*", "", line, flags=re.IGNORECASE)
        # Support legacy lines that include a speaker label before the spoken text.
        if ":" in line:
            possible_prefix, remainder = line.split(":", 1)
            if len(possible_prefix) <= 40 and not any(ch in possible_prefix for ch in "।!?"):
                line = remainder.strip()
        if len(line) >= 2 and line[0] in ('"', "“") and line[-1] in ('"', "”"):
            line = line[1:-1].strip()
        if line:
            scenes.append((number, line))
    return scenes

def main():
    if not HF_TOKEN:
        raise SystemExit("HF_TOKEN secret is missing. Add your Hugging Face read token as a GitHub Actions secret named HF_TOKEN.")
    if not MD_PATH.exists():
        raise SystemExit(f"Episode Markdown not found: {MD_PATH}")
    HfApi(token=HF_TOKEN).model_info(MODEL_ID)
    scenes = extract_scenes(MD_PATH.read_text(encoding="utf-8"))
    if not scenes:
        raise SystemExit("No Telugu Character Dialogue lines found in the episode Markdown.")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Found {len(scenes)} dialogue lines; output folder: {OUT_DIR}", flush=True)
    device = "cpu"
    print("GitHub runner has no guaranteed GPU; using CPU. This may take a long time.", flush=True)
    model = ParlerTTSForConditionalGeneration.from_pretrained(MODEL_ID, token=HF_TOKEN).to(device)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
    desc_name = model.config.text_encoder._name_or_path
    description_tokenizer = AutoTokenizer.from_pretrained(desc_name, token=HF_TOKEN)
    description_inputs = description_tokenizer(VOICE_DESCRIPTION, return_tensors="pt")
    completed, failures = [], []
    for number, text in scenes:
        path = OUT_DIR / f"scene_{number:03d}.wav"
        if path.exists() and path.stat().st_size > 1000:
            print(f"Scene {number:02d}: already complete; skipping", flush=True)
            completed.append((number, path))
            continue
        try:
            prompt_inputs = tokenizer(text, return_tensors="pt")
            with torch.inference_mode():
                generated = model.generate(
                    input_ids=description_inputs.input_ids,
                    attention_mask=description_inputs.attention_mask,
                    prompt_input_ids=prompt_inputs.input_ids,
                    prompt_attention_mask=prompt_inputs.attention_mask,
                )
            audio = generated.detach().float().cpu().numpy().squeeze()
            if audio.size == 0:
                raise RuntimeError("Model returned empty audio.")
            sf.write(str(path), audio, model.config.sampling_rate)
            completed.append((number, path))
            print(f"Scene {number:02d}: PASS ({len(audio)/model.config.sampling_rate:.1f}s)", flush=True)
            del generated, audio, prompt_inputs
            gc.collect()
        except Exception as exc:
            failures.append((number, str(exc)))
            print(f"Scene {number:02d}: FAILED: {exc}", flush=True)
    with (OUT_DIR / "duration_report.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["scene", "duration_seconds", "file"])
        for number, path in completed:
            info = sf.info(str(path))
            writer.writerow([number, round(info.duration, 2), path.name])
    print(f"Audio generation finished: {len(completed)}/{len(scenes)} scenes.", flush=True)
    if failures:
        print("Failures:", failures, flush=True)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
