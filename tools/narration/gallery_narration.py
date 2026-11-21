"""Prepare and render four-part Gallery narration, with no install dependencies."""
import argparse
from contextlib import contextmanager
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

VOICE = "en-AU-Chirp3-HD-Callirrhoe"
RATE = 0.9
ENDPOINT = "https://texttospeech.googleapis.com/v1/text:synthesize"
PARTS = (("intro", "constellation"), ("discoverer", "discoverer"),
         ("science", "moon"), ("scope", "scope"))
MAX_RESPONSE = 4 * 1024 * 1024

class NarrationError(Exception):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def atomic_write(path, data):
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(dir=path.parent, delete=False) as f:
        tmp = Path(f.name)
        try:
            f.write(data)
        except BaseException:
            f.close()
            tmp.unlink(missing_ok=True)
            raise
    try:
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)

def write_json(path, data):
    atomic_write(path, (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

def load_script(path):
    s = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(s, dict) or s.get("schema") != 1:
        raise NarrationError("Choose a schema-1 Gallery narration JSON file.")
    label, ident, captured = (s.get(k) for k in ("label", "image_id", "captured"))
    if not isinstance(label, str) or not label.strip() or label != label.strip():
        raise NarrationError("An exact Gallery label is required.")
    if not isinstance(ident, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", ident):
        raise NarrationError("Invalid image ID.")
    if not isinstance(captured, str) or not re.fullmatch(r"\d{4}-(?:0[1-9]|1[0-2])", captured):
        raise NarrationError("Capture date must be YYYY-MM (no individual days).")
    blocks = s.get("spoken_script")
    if not isinstance(blocks, dict) or set(blocks) != {name for name, _ in PARTS}:
        raise NarrationError("Script must have exactly intro, discoverer, science and scope.")
    if s.get("status") not in ("draft", "approved"):
        raise NarrationError("Status must be draft or approved.")
    for name, value in blocks.items():
        if not isinstance(value, str) or not value.strip() or len(value.encode("utf-8")) > 4500:
            raise NarrationError(f"{name}: missing or over the 4,500-byte safety cap.")
    scope = blocks["scope"]
    months = "January February March April May June July August September October November December".split()
    month_name = months[int(captured[5:])-1]
    if not re.search(rf"\b{month_name}\s+{captured[:4]}\b", scope, re.I):
        raise NarrationError(f"Scope must say {month_name} {captured[:4]}.")
    if re.search(rf"\b(?:\d{{1,2}}(?:st|nd|rd|th)?\s+{month_name}|{month_name}\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,|\b))\b|\b\d{{4}}[-/]\d{{1,2}}[-/]\d{{1,2}}\b", scope, re.I):
        raise NarrationError("Scope contains a possible exact capture date.")
    return s

def plan(script):
    rows, files = [], []
    for i, (name, overlay) in enumerate(PARTS, 1):
        file = f"{script['image_id']}_{i:02}_{name}.mp3"
        text = script["spoken_script"][name].strip()
        config = {"input": {"text": text}, "voice": {"languageCode": "en-AU", "name": VOICE},
                  "audioConfig": {"audioEncoding": "MP3", "speakingRate": RATE}}
        sig = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
        rows.append((file, config, sig))
        part = {"file": "audio/" + file, "show": overlay}
        if overlay == "moon":
            part["hold_s"] = 4
        files.append(part)
    return rows, {"image_id": script["image_id"], "voice": f"Google TTS {VOICE}", "parts": files}

def mp3_check(data):
    if not 1024 < len(data) <= MAX_RESPONSE:
        raise NarrationError("The audio file is empty, too short or too large.")
    start = 0
    if data[:3] == b"ID3":
        sizes = data[6:10]
        if any(n >= 128 for n in sizes):
            raise NarrationError("Invalid MP3 metadata header.")
        start = 10 + sum(n << shift for n, shift in zip(sizes, (21, 14, 7, 0)))
    # Check the first MPEG Layer III frame header. Full decode is a separate publication check.
    frame = data[start:start+4]
    if (len(frame) != 4 or frame[0] != 0xff or (frame[1] & 0xe0) != 0xe0
            or (frame[1] & 0x18) == 0x08 or (frame[1] & 0x06) != 0x02
            or (frame[2] >> 4) in (0, 15) or (frame[2] & 12) == 12):
        raise NarrationError("The returned file is not a recognised MP3.")

def synthesize(key, config):
    req = urllib.request.Request(ENDPOINT, json.dumps(config).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=45) as r:
            result = json.loads(r.read(MAX_RESPONSE * 2 + 1))
        data = base64.b64decode(result["audioContent"], validate=True)
    except urllib.error.HTTPError as exc:
        raise NarrationError(f"Google returned HTTP {exc.code}. Check the existing project's key, API access and quota. No automatic retries.") from None
    except (OSError, KeyError, TypeError, ValueError):
        raise NarrationError("Google's audio request did not succeed or returned invalid data. No automatic retries.") from None
    mp3_check(data)
    return data

def process(path, output, *, mode="plan", key=None, max_chars=6000, fetch=synthesize):
    s = load_script(path)
    rows, record = plan(s)
    if mode == "render" and s["status"] != "approved":
        raise NarrationError("Full render needs an approved script. Use the single-clip voice test first.")
    selected = rows[:1] if mode == "sample" else rows
    count = sum(len(row[1]["input"]["text"]) for row in selected)
    if count > max_chars:
        raise NarrationError(f"Script exceeds this run's {max_chars:,}-character limit.")
    if mode != "plan" and not key:
        raise NarrationError("No Google voice key found on this computer. Use the existing Ryzen setup.")
    out = Path(output) / s["image_id"]
    out.mkdir(parents=True, exist_ok=True)
    if mode == "plan":
        write_json(out / "plan.json", {"label": s["label"], "status": s["status"], "voice": VOICE,
                                     "speaking_rate": RATE, "characters": count, "narration": record})
        return out, count, 0
    with render_lock(out):
        return render(out, s, selected, record, mode, key, count, fetch)

@contextmanager
def render_lock(out):
    lock = out / ".rendering"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise NarrationError("Another render is running or was interrupted. Choose a new output folder if the old job is no longer running.") from None
    os.close(descriptor)
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)

def render(out, s, selected, record, mode, key, count, fetch):
    previous = {}
    manifest = out / "verified-audio.json"
    if manifest.is_file():
        previous = json.loads(manifest.read_text(encoding="utf-8")).get("files", {})
    done = {}
    generated = 0
    for name, cfg, sig in selected:
        dest = out / name
        old = previous.get(name, {})
        if dest.is_file():
            data = dest.read_bytes()
            if old != {"input": sig, "sha256": hashlib.sha256(data).hexdigest()}:
                raise NarrationError(f"{name} already exists but does not match this script. Choose a new output folder; no file was overwritten.")
            mp3_check(data)
        else:
            data = fetch(key, cfg)
            mp3_check(data)
            atomic_write(dest, data)
            generated += 1
        done[name] = {"input": sig, "sha256": hashlib.sha256(data).hexdigest()}
        # Commit each successful local result so a retry does not call Google for it again.
        write_json(manifest, {"files": {**previous, **done}})
    if mode == "render":
        write_json(out / "gallery-record.json", {"label": s["label"], "narration": record,
                                                "files": done})
    return out, count, generated

def gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox
    root = tk.Tk()
    root.withdraw()
    choice = messagebox.askyesnocancel("Gallery narration",
        "Yes: make a one-clip voice test.\nNo: render all four parts of an approved script.\nCancel: exit.\n\nUses the Google project already configured on this PC. Nothing is published.")
    if choice is None:
        return 0
    script = filedialog.askopenfilename(title="Choose the narration script", filetypes=[("Narration JSON", "*.json")])
    if not script:
        return 0
    key = os.getenv("GOOGLE_TTS_KEY")
    if not key and sys.platform == "win32":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as handle:
                key = winreg.QueryValueEx(handle, "GOOGLE_TTS_KEY")[0]
        except OSError:
            pass
    try:
        if not key:
            raise NarrationError("No Google voice key found on this computer. Use the existing Ryzen setup.")
        output = Path(script).parent / "Gallery voice output"
        if not choice:
            document = load_script(script)
            if document["status"] == "draft":
                # Approval is explicit, tied to the exact text shown, and never changes the draft.
                body = "\n\n".join(f"{part.title()}: {document['spoken_script'][part]}" for part, _ in PARTS)
                if len(body) > 2100:
                    raise NarrationError("This draft is too long for the on-screen review. Use an already approved script.")
                if not messagebox.askokcancel("Review the four parts", body + "\n\nOK approves these words and starts rendering. Nothing is published."):
                    return 0
                approved = output / document["image_id"] / "approved-script.json"
                approved.parent.mkdir(parents=True, exist_ok=True)
                document["status"] = "approved"
                write_json(approved, document)
                script = approved
        target, _, _ = process(script, output, mode="sample" if choice else "render", key=key)
    except (NarrationError, OSError, ValueError) as exc:
        messagebox.showerror("Gallery narration", str(exc))
        return 1
    messagebox.showinfo("Gallery narration", f"Audio saved to:\n{target}\n\nNothing uploaded.")
    if sys.platform == "win32":
        os.startfile(target)
    return 0

def main():
    if len(sys.argv) == 1 and sys.platform == "win32":
        return gui()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("plan", "sample", "render"))
    p.add_argument("script", type=Path)
    p.add_argument("--out", type=Path, default=Path("gallery-voice-output"))
    args = p.parse_args()
    try:
        target, count, generated = process(args.script, args.out, mode=args.mode, key=os.getenv("GOOGLE_TTS_KEY"))
    except (NarrationError, OSError, ValueError) as exc:
        p.exit(1, f"No publication: {exc}\n")
    print(f"{target}: {count:,} characters in selection, {generated} clip(s) generated. Nothing published.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
