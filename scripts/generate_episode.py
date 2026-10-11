#!/usr/bin/env python3
"""TELUGU DEVOTEE episode package generator.

Flow (all through the Gemini API, no extra pip packages):
  1. Beat plan  : one short line per scene, so the story is paced across all scenes.
  2. Scene batches: BATCH_SIZE scenes per call (default 10), each call sees the
     previous scene for continuity. Every batch is validated (right scene
     numbers, right count) and retried if the model cut off or skipped scenes.
  3. SEO package: titles, description, tags, thumbnail, hook options.

Output: output/episode_package.md (rewritten after every step, so a partial
result survives a failure).
"""
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output" / "episode_package.md"

API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()
EPISODE = os.environ.get("EPISODE_NUMBER", "2").strip()
TITLE = os.environ.get("EPISODE_TITLE", "").strip()
OUTLINE = os.environ.get("STORY_OUTLINE", "").strip()
TOTAL = int(os.environ.get("TOTAL_SCENES", "60"))
BATCH = int(os.environ.get("BATCH_SIZE", "10"))
OFFSET = int(os.environ.get("SCENE_OFFSET", "0") or 0)  # label = OFFSET + local number
BATCH_TOKENS = int(os.environ.get("BATCH_MAX_TOKENS", "20000"))
MAX_ATTEMPTS = 3

RETRY_CODES = (408, 429, 500, 502, 503, 504)


class GenError(Exception):
    pass


def read_text(path):
    if not path.exists():
        print(f"WARNING: missing file {path}")
        return ""
    text = path.read_text(encoding="utf-8").strip()
    # strip optional YAML front matter
    return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S).strip()


def call_gemini(prompt, max_tokens, temperature=0.8):
    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{MODEL}:generateContent"
    )
    body = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }).encode("utf-8")

    result = None
    for attempt in range(5):
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json", "x-goog-api-key": API_KEY},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as err:
            details = err.read().decode("utf-8", errors="replace")
            if err.code in RETRY_CODES and attempt < 4:
                delay = 2 ** (attempt + 1) + random.random()
                print(f"HTTP {err.code}; retrying in {delay:.1f}s")
                time.sleep(delay)
                continue
            hint = ""
            if err.code in (400, 404):
                hint = f" (check that model '{MODEL}' exists for your API key)"
            raise GenError(f"Gemini HTTP {err.code}{hint}: {details[:1500]}")
        except (urllib.error.URLError, TimeoutError) as err:
            if attempt < 4:
                delay = 2 ** (attempt + 1) + random.random()
                print(f"Network error ({err}); retrying in {delay:.1f}s")
                time.sleep(delay)
                continue
            raise GenError(f"Network error: {err}")

    if result is None:
        raise GenError("Gemini request failed.")
    candidates = result.get("candidates", [])
    if not candidates:
        raise GenError(
            "No candidates: "
            + json.dumps(result.get("promptFeedback", {}), ensure_ascii=False)
        )
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "\n".join(
        p["text"] for p in parts if isinstance(p, dict) and "text" in p
    ).strip()
    return text, candidates[0].get("finishReason", "")


# ---------------------------------------------------------------- beat plan
def make_beat_plan():
    prompt = f"""You are planning a Telugu Ramayanam episode for the YouTube channel TELUGU DEVOTEE.

EPISODE {EPISODE}: {TITLE}

STORY OUTLINE:
{OUTLINE}

Plan exactly {TOTAL} scenes of 10 seconds each. Follow Valmiki Ramayanam only;
never invent events. Pace the outline so it fills all {TOTAL} scenes, with a
tense hook in scenes 1-2 and a story-relevant cliffhanger in the last scene.

Output ONLY a numbered list from 1 to {TOTAL}, one line per scene, exactly:
N. SPEAKER | PLACE | one-line description of what happens and what is said (English)
One speaker per scene. No intro, no outro, no blank numbering gaps."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        text, finish = call_gemini(prompt, 8000, temperature=0.6)
        beats = {}
        for line in text.splitlines():
            m = re.match(r"^\s*(\d+)[.)]\s+(.*\S)\s*$", line)
            if m:
                beats[int(m.group(1))] = m.group(2)
        if sorted(beats) == list(range(1, TOTAL + 1)):
            return beats
        print(
            f"Beat plan attempt {attempt}: got {len(beats)} beats "
            f"(finish={finish}); retrying."
        )
    raise GenError(f"Could not get a valid {TOTAL}-beat plan.")


# ------------------------------------------------------------ scene batches
def make_batch(start, end, beats, prev_tail, script_skill, locks):
    expected = [OFFSET + n for n in range(start, end + 1)]
    beat_lines = "\n".join(f"{OFFSET + n}. {beats[n]}" for n in range(start, end + 1))
    extra = ""
    if start == 1:
        extra += (
            "\nThis batch opens the episode: scenes "
            f"{expected[0]}-{expected[1]} are the hook, a tense moment taken "
            "from the text, not a summary."
        )
    if end == TOTAL:
        extra += (
            "\nThis batch ends the episode: the last scene must be a "
            "story-relevant cliffhanger."
        )
    prompt = f"""You are the Telugu Ramayanam screenwriter for TELUGU DEVOTEE.

SCRIPT RULES (follow exactly):
{script_skill}

LOCKS (paste the relevant CHARACTER LOCK text and the STYLE LOCK text into EVERY IMAGE PROMPT):
{locks}

EPISODE {EPISODE}: {TITLE}

STORY OUTLINE (context only):
{OUTLINE}

BEATS FOR THIS BATCH (write exactly one scene per beat, in this order):
{beat_lines}

PREVIOUS SCENE (for continuity; do not repeat it):
{prev_tail or "none - this is the first batch"}
{extra}

Write exactly {len(expected)} scenes, numbered {expected[0]} to {expected[-1]}.
Begin each scene with this exact header line:
### SCENE <number> | <speaker> | <place>
Then, in order: IMAGE PROMPT, MOTION PROMPT (0-3s / 3-6s / 6-10s), DIALOGUE (Telugu script), LIP-SYNC.
Do not summarize or skip scenes. Output only the scenes, no intro or outro."""
    last_text = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        text, finish = call_gemini(prompt, BATCH_TOKENS)
        found = [
            int(n) for n in re.findall(r"^#{1,4}\s*\**SCENE\s+(\d+)", text, re.M | re.I)
        ]
        last_text = text
        if found == expected and finish != "MAX_TOKENS":
            return text, True
        print(
            f"Batch {expected[0]}-{expected[-1]} attempt {attempt}: "
            f"found {found}, finish={finish}; retrying."
        )
    return last_text, False


# --------------------------------------------------------------------- SEO
def make_seo(beats, seo_skill):
    beat_summary = "\n".join(f"{n}. {beats[n]}" for n in sorted(beats))
    prompt = f"""You are the YouTube SEO specialist for TELUGU DEVOTEE (Telugu Ramayanam channel).

SEO RULES (follow exactly):
{seo_skill}

EPISODE {EPISODE}: {TITLE}

SCENE BEATS (the only facts you may use about the episode):
{beat_summary}

Return Markdown with these sections, in this order:
1. Three hook options for scenes 1-2 (tense moments from the text)
2. Three target search queries this video should win
3. Three Telugu titles, three Telugu-English titles, one recommended title
4. Description in Telugu and in English (first two lines carry the search words)
5. Hashtags, and at most 15 comma-separated tags
6. Pinned comment and one community post
7. Thumbnail concept with Telugu text, and a thumbnail image prompt
8. A promotional Short opening hook
Do not promise views or virality. Never invent a number, result or source.
End with exactly one ask and the last line: ship it, or change it?"""
    text, finish = call_gemini(prompt, 12000, temperature=0.7)
    if finish == "MAX_TOKENS":
        text += "\n\n> WARNING: SEO section hit the token limit and may be incomplete."
    return text


# ------------------------------------------------------------------- main
def write_package(parts):
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n\n".join(parts).strip() + "\n", encoding="utf-8")


def main():
    if not API_KEY:
        raise SystemExit("ERROR: GEMINI_API_KEY secret is missing.")
    if not TITLE or not OUTLINE:
        raise SystemExit("ERROR: EPISODE_TITLE and STORY_OUTLINE are required.")

    script_skill = read_text(ROOT / "skills" / "yt-script" / "SKILL.md")
    locks = read_text(ROOT / "skills" / "yt-script" / "locks.md")
    seo_skill = read_text(ROOT / "skills" / "yt-seo" / "SKILL.md")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts = [
        f"# TELUGU DEVOTEE - Episode {EPISODE}: {TITLE}\n"
        f"Generated {now} | model {MODEL} | scenes {OFFSET + 1}-{OFFSET + TOTAL}"
    ]
    failed = []

    print("Step 1/3: beat plan")
    try:
        beats = make_beat_plan()
    except GenError as err:
        raise SystemExit(f"ERROR: {err}")
    parts.append(
        "## Beat plan\n"
        + "\n".join(f"{OFFSET + n}. {beats[n]}" for n in sorted(beats))
    )
    write_package(parts)

    print("Step 2/3: scene batches")
    prev_tail = ""
    for start in range(1, TOTAL + 1, BATCH):
        end = min(start + BATCH - 1, TOTAL)
        print(f"  scenes {OFFSET + start}-{OFFSET + end}")
        try:
            text, ok = make_batch(start, end, beats, prev_tail, script_skill, locks)
        except GenError as err:
            failed.append(f"{OFFSET + start}-{OFFSET + end}: {err}")
            break
        if not ok:
            failed.append(f"{OFFSET + start}-{OFFSET + end}: validation failed")
            text = (
                f"> WARNING: scenes {OFFSET + start}-{OFFSET + end} did not pass "
                "validation (wrong scene numbers or cut off). Review or rerun.\n\n"
                + text
            )
        parts.append(text)
        prev_tail = text[-1500:]
        write_package(parts)

    print("Step 3/3: SEO package")
    try:
        parts.append("## SEO and packaging\n" + make_seo(beats, seo_skill))
    except GenError as err:
        failed.append(f"SEO: {err}")
    write_package(parts)

    print(f"Saved {OUTPUT} ({OUTPUT.stat().st_size} bytes)")
    if failed:
        print("PROBLEMS:\n  " + "\n  ".join(failed))
        sys.exit(1)
    print("SUCCESS")


if __name__ == "__main__":
    main()
