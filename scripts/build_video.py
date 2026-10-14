#!/usr/bin/env python3
"""Submit an existing TELUGU DEVOTEE Markdown script to a configured MoneyPrinterTurbo API.

This script creates a video file for human review only. It never publishes to YouTube.
Required environment variables: MPT_API_URL, VIDEO_SUBJECT, SCRIPT_PATH.
Optional: MPT_API_KEY, VIDEO_ASPECT, OUTPUT_DIR.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (ROOT / os.getenv("SCRIPT_PATH", "output/episode_package.md")).resolve()
OUTPUT_DIR = (ROOT / os.getenv("OUTPUT_DIR", "output/moneyprinterturbo")).resolve()
SUBJECT = os.getenv("VIDEO_SUBJECT", "TELUGU DEVOTEE Ramayanam").strip()
ASPECT = os.getenv("VIDEO_ASPECT", "16:9").strip()
API_URL = os.getenv("MPT_API_URL", "").strip().rstrip("/")
API_KEY = os.getenv("MPT_API_KEY", "").strip()
POLL_SECONDS = 10
TIMEOUT_SECONDS = 50 * 60

TELUGU_RE = re.compile(r"[\u0c00-\u0c7f]")
SKIP_RE = re.compile(
    r"^(?:#{1,6}\s*)?(?:image prompt|motion prompt|voice prompt|character lock|"
    r"style lock|seo|hashtags|tags|thumbnail|negative prompt|visual prompt)\b",
    re.IGNORECASE,
)
DIALOGUE_LABEL_RE = re.compile(
    r"^(?:telugu\s+)?(?:dialogue|spoken dialogue|voice line|dialogue \(telugu\)|"
    r"డైలాగ్|సంభాషణ|మాటలు)\s*[:：-]\s*",
    re.IGNORECASE,
)


def fail(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def extract_telugu_script(markdown: str) -> str:
    """Prefer explicitly labelled dialogue lines; otherwise retain clean Telugu prose.

    Prompt/production sections are excluded so image and motion instructions are not
    accidentally read aloud by the voiceover engine.
    """
    lines = markdown.splitlines()
    labelled: list[str] = []
    for raw in lines:
        line = raw.strip().strip("`*_> ")
        match = DIALOGUE_LABEL_RE.match(line)
        if match:
            text = line[match.end():].strip()
            if text and TELUGU_RE.search(text):
                labelled.append(text)

    if labelled:
        return "\n".join(labelled)

    clean: list[str] = []
    in_prompt_block = False
    for raw in lines:
        line = raw.strip().strip("`> ")
        if not line:
            continue
        if SKIP_RE.match(line):
            in_prompt_block = True
            continue
        if re.match(r"^(?:#{1,6}\s*)?(?:scene\s+\d+|సీన్\s*\d+)", line, re.IGNORECASE):
            in_prompt_block = False
            continue
        # English production prompt paragraphs should never be spoken.
        if in_prompt_block and not TELUGU_RE.search(line):
            continue
        if not TELUGU_RE.search(line):
            continue
        if line.startswith(("#", "|", "![", "[")):
            continue
        if len(line) > 700:
            continue
        clean.append(line)

    # Deduplicate identical lines while preserving order.
    unique = list(dict.fromkeys(clean))
    return "\n".join(unique)


def request_json(url: str, payload: dict | None = None, method: str = "GET") -> dict:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if API_KEY:
        headers["x-api-key"] = API_KEY
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")[:1500]
        fail(f"MoneyPrinterTurbo API returned HTTP {exc.code}: {details}")
    except urllib.error.URLError as exc:
        fail(f"Cannot reach MoneyPrinterTurbo API at {url}: {exc.reason}")
    except TimeoutError:
        fail(f"Request timed out while contacting MoneyPrinterTurbo API at {url}")
    return {}


def unwrap(response: dict) -> dict:
    if not isinstance(response, dict):
        fail("Unexpected API response format.")
    if response.get("status", 200) not in (200, 201):
        fail(f"MoneyPrinterTurbo API error: {response.get('message', response)}")
    data = response.get("data", response)
    if not isinstance(data, dict):
        fail("API response did not contain an object in 'data'.")
    return data


def download_video(url: str, destination: Path) -> None:
    # MPT may return a relative /tasks/... URL or an absolute URL.
    resolved = urllib.parse.urljoin(API_URL + "/", url)
    parsed = urllib.parse.urlparse(resolved)
    base = urllib.parse.urlparse(API_URL)
    if parsed.scheme not in ("http", "https") or parsed.netloc != base.netloc:
        fail("Refusing to download a video from an unexpected host returned by the API.")
    headers = {}
    if API_KEY:
        headers["x-api-key"] = API_KEY
    req = urllib.request.Request(resolved, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as response, destination.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
    except Exception as exc:
        destination.unlink(missing_ok=True)
        fail(f"Could not download generated video: {exc}")
    if not destination.exists() or destination.stat().st_size < 1024:
        destination.unlink(missing_ok=True)
        fail("The API returned a video file that is empty or unexpectedly small.")


def main() -> None:
    if not API_URL:
        fail("Set repository Actions secrets MPT_API_URL and MPT_API_KEY first. MPT_API_URL must be the base URL of a running, reachable MoneyPrinterTurbo server.")
    if not API_URL.startswith(("https://", "http://")):
        fail("MPT_API_URL must start with https:// or http://.")
    if ASPECT not in {"16:9", "9:16", "1:1"}:
        fail("VIDEO_ASPECT must be 16:9, 9:16, or 1:1.")
    if not SCRIPT_PATH.is_file():
        fail(f"Script file not found: {SCRIPT_PATH.relative_to(ROOT) if SCRIPT_PATH.is_relative_to(ROOT) else SCRIPT_PATH}")
    markdown = SCRIPT_PATH.read_text(encoding="utf-8")
    script = extract_telugu_script(markdown)
    if len(script) < 30:
        fail("Could not extract enough Telugu dialogue/prose from the selected Markdown. Use labelled 'Dialogue:' / 'డైలాగ్:' lines or point SCRIPT_PATH to a clean Telugu script file.")
    if len(script) > 18000:
        script = script[:18000]
        print("WARNING: extracted script exceeded 18,000 characters and was trimmed for a first test.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Persist the exact submitted text for review/debugging, not any credentials.
    (OUTPUT_DIR / "submitted_telugu_script.txt").write_text(script + "\n", encoding="utf-8")
    payload = {
        "video_subject": SUBJECT,
        "video_script": script,
        "video_aspect": ASPECT,
        "video_language": "te-IN",
        "video_source": "pexels",
        "video_clip_duration": 5,
        "video_count": 1,
        "match_materials_to_script": True,
        "video_concat_mode": "sequential",
        "voice_name": "te-IN-ShrutiNeural",
        "voice_rate": 1.0,
        "voice_volume": 1.0,
        "bgm_type": "random",
        "bgm_volume": 0.12,
        "subtitle_enabled": True,
        "subtitle_display_mode": "sentence",
        "font_size": 48,
        "text_fore_color": "#FFFFFF",
        "stroke_color": "#000000",
        "stroke_width": 2,
        "n_threads": 2,
    }
    print(f"Submitting one review video: {SUBJECT!r}, aspect={ASPECT}, script_chars={len(script)}")
    created = unwrap(request_json(API_URL + "/api/v1/videos", payload, method="POST"))
    task_id = created.get("task_id")
    if not task_id:
        fail("API did not return a task_id; check the MoneyPrinterTurbo API version and /docs.")
    print(f"MoneyPrinterTurbo task created: {task_id}")

    deadline = time.monotonic() + TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        time.sleep(POLL_SECONDS)
        status = unwrap(request_json(API_URL + "/api/v1/tasks/" + urllib.parse.quote(str(task_id), safe="")))
        state = status.get("state")
        progress = status.get("progress", 0)
        print(f"Task state={state}, progress={progress}%")
        if state == -1:
            fail(f"Video generation failed at stage {status.get('failed_stage', 'unknown')}: {status.get('error', 'No error details returned')}")
        if state == 1:
            videos = status.get("combined_videos") or status.get("videos") or []
            if not videos:
                fail("Task completed but the API returned no video URL.")
            for index, video_url in enumerate(videos, start=1):
                target = OUTPUT_DIR / f"review-video-{index}.mp4"
                download_video(str(video_url), target)
                print(f"Downloaded review video: {target.relative_to(ROOT)} ({target.stat().st_size} bytes)")
            (OUTPUT_DIR / "REVIEW_REQUIRED.txt").write_text(
                "Human review required. This workflow does not publish to YouTube.\n"
                "Check Telugu pronunciation, story accuracy, visuals, subtitles, music, and rights before uploading.\n",
                encoding="utf-8",
            )
            return
    fail(f"Timed out after {TIMEOUT_SECONDS // 60} minutes. Check the task in MoneyPrinterTurbo WebUI/API.")


if __name__ == "__main__":
    main()
