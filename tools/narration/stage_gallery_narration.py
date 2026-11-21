"""Verify a rendered set and prepare a reviewable Gallery patch without changing the repo."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from gallery_narration import NarrationError, load_script, mp3_check, plan, write_json

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def stage(script_file, rendered, repo, output):
    script = load_script(script_file)
    if script["status"] != "approved":
        raise NarrationError("The narration must be approved before staging.")
    rows, record = plan(script)
    result = read(rendered / "gallery-record.json")
    expected = {"label": script["label"], "narration": record, "files": result.get("files")}
    if result != expected or not isinstance(result["files"], dict):
        raise NarrationError("The audio record does not match the approved script.")
    assets = read(repo / "assets.json")
    label = assets["labels"].get(script["label"])
    if not label:
        raise NarrationError("No matching Gallery label.")
    if label.get("narration"):
        raise NarrationError("This item already has narration. An explicit replacement is separate.")
    matches = [i for i in read(repo / "gallery.json") if i.get("label") == script["label"]]
    if len(matches) != 1 or matches[0].get("captured") != script["captured"]:
        raise NarrationError("Gallery metadata or capture month differs from the approved script.")
    scope = matches[0].get("scope")
    site = matches[0].get("site", matches[0].get("location"))
    scope_overlay = assets.get("site_scopes", {}).get(site, {}).get(scope) or assets["scopes"].get(scope)
    for overlay in (assets["constellations"].get(label.get("constellation")),
                    assets["people"].get(label.get("person")), scope_overlay, {"file": "moon.png"}):
        relative = (overlay or {}).get("file")
        if not relative or not (repo / relative).is_file():
            raise NarrationError("A constellation, portrait, Moon or scope asset is missing.")
    if output.exists():
        raise NarrationError("Choose a new patch output folder.")
    if not shutil.which("ffmpeg"):
        raise NarrationError("Full audio decoding needs ffmpeg on the staging computer.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as temp:
        patch = Path(temp) / "patch"
        (patch / "audio").mkdir(parents=True)
        for name, _, config_hash in rows:
            if (repo / "audio" / name).exists():
                raise NarrationError(f"Audio filename already in use: {name}")
            data = (rendered / name).read_bytes()
            mp3_check(data)
            if result["files"].get(name) != {"input": config_hash, "sha256": hashlib.sha256(data).hexdigest()}:
                raise NarrationError(f"Audio or script hash mismatch: {name}")
            dest = patch / "audio" / name
            dest.write_bytes(data)
            decoded = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", str(dest), "-f", "null", "-"],
                                     capture_output=True, timeout=60)
            if decoded.returncode:
                raise NarrationError(f"Audio decode failed: {name}")
        label["narration"] = record
        write_json(patch / "assets.json", assets)
        patch.rename(output)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for field in ("script", "rendered", "gallery_checkout", "output_patch"):
        p.add_argument(field, type=Path)
    args = p.parse_args()
    try:
        stage(args.script, args.rendered, args.gallery_checkout, args.output_patch)
    except (NarrationError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        p.exit(1, f"No publication: {exc}\n")
    print(f"Verified assets and decoded all four clips. Gallery patch staged at {args.output_patch}; nothing published.")

if __name__ == "__main__":
    main()
