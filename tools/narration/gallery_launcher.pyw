"""Double-click on Windows to review and render Gallery narration in one batch."""
import base64
import ctypes
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import gallery_narration as renderer

def local_key_path():
    return Path(os.environ["LOCALAPPDATA"]) / "AstroTTS" / "google-tts.dpapi"

def dpapi(payload, protect):
    if sys.platform != "win32":
        raise OSError("The Windows key store is available only on the Ryzen.")
    from ctypes import wintypes as w
    class Blob(ctypes.Structure):
        _fields_ = [("size", w.DWORD), ("data", ctypes.POINTER(ctypes.c_ubyte))]
    buf = (ctypes.c_ubyte * len(payload)).from_buffer_copy(payload)
    src, dst = Blob(len(buf), buf), Blob()
    crypt = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    action = crypt.CryptProtectData if protect else crypt.CryptUnprotectData
    action.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.POINTER(Blob),
                       ctypes.c_void_p, ctypes.c_void_p, w.DWORD, ctypes.POINTER(Blob)]
    action.restype = w.BOOL
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    try:
        if not action(ctypes.byref(src), None, None, None, None, 1, ctypes.byref(dst)):
            raise ctypes.WinError(ctypes.get_last_error())
        return ctypes.string_at(dst.data, dst.size)
    finally:
        ctypes.memset(buf, 0, len(buf))
        if dst.data:
            ctypes.memset(dst.data, 0, dst.size)
            kernel.LocalFree(dst.data)

def save_key(key, path=None):
    if not key or not key.isascii() or any(c.isspace() for c in key):
        raise ValueError("Paste the key only, with no spaces.")
    path = local_key_path() if path is None else path
    data = dpapi(key.encode("ascii"), True)
    path.parent.mkdir(parents=True, exist_ok=True)
    renderer.atomic_write(path, data)

def read_key(path=None):
    path = local_key_path() if path is None else path
    if not path.exists():
        return None
    data = path.read_bytes()
    if not 0 < len(data) < 8192:
        raise ValueError("The saved key is unreadable. Use Set or replace key.")
    return dpapi(data, False).decode("ascii")

def load_batch(path):
    if path.stat().st_size > 160000:
        raise ValueError("Choose a narration script or batch JSON, not an audio upload.")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list) or not 1 <= len(data) <= 6:
        raise ValueError("Choose a batch with one to six narration scripts.")
    items, seen, labels, total = [], set(), set(), 0
    with TemporaryDirectory() as d:
        for obj in data:
            f = Path(d) / "draft.json"
            renderer.write_json(f, obj)
            s = renderer.load_script(f)
            if s["image_id"] in seen or s["label"] in labels:
                raise ValueError("A Gallery target or image ID appears twice.")
            seen.add(s["image_id"])
            labels.add(s["label"])
            total += sum(len(t.strip()) for t in s["spoken_script"].values())
            items.append(s)
    if total > 6000:
        raise ValueError("This batch exceeds the 6,000-character limit.")
    return items, total

def render_batch(items, output, key, fetch=renderer.synthesize):
    output.mkdir(parents=True, exist_ok=True)
    bundle = []
    with TemporaryDirectory(dir=output) as d:
        f = Path(d) / "approved.json"
        for draft in items:
            script = {**draft, "status": "approved"}
            renderer.write_json(f, script)
            clip_dir, _, _ = renderer.process(f, output, mode="render", key=key, fetch=fetch)
            record = json.loads((clip_dir / "gallery-record.json").read_text(encoding="utf-8"))
            audio = {}
            for part in record["narration"]["parts"]:
                name = Path(part["file"]).name
                audio[name] = base64.b64encode((clip_dir / name).read_bytes()).decode("ascii")
            bundle.append({"record": record, "audio": audio})
    out = output / "Gallery-narration-upload.json"
    renderer.write_json(out, bundle)
    return out

def gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog
    from tkinter.scrolledtext import ScrolledText

    root = tk.Tk()
    root.title("Gallery Voice")
    project = Path(__file__).resolve().parent
    status = tk.StringVar(value="Choose a narration JSON from Astra.")

    def set_key():
        key = simpledialog.askstring("Gallery Voice", "Paste your Google Text-to-Speech API key.\nIt will be saved securely for this Windows account.", show="*", parent=root)
        if key is None:
            return None
        try:
            key = key.strip()
            save_key(key)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Gallery Voice", str(exc), parent=root)
            return None
        status.set("Key saved. It stays on this PC.")
        return key

    def review(items, total):
        win = tk.Toplevel(root)
        win.title("Review the narration")
        win.transient(root)
        panel = ScrolledText(win, width=80, height=23, wrap="word")
        panel.pack(fill="both", expand=True, padx=12, pady=12)
        for item in items:
            panel.insert("end", item["label"] + "\n\n")
            for part, _ in renderer.PARTS:
                panel.insert("end", part.title() + ": " + item["spoken_script"][part] + "\n\n")
        panel.config(state="disabled")
        allowed = []
        def accept():
            allowed.append(True)
            win.destroy()
        tk.Button(win, text=f"Approve and render ({total:,} characters)", command=accept).pack(side="left", padx=12, pady=8)
        tk.Button(win, text="Cancel", command=win.destroy).pack(side="right", padx=12, pady=8)
        win.grab_set()
        root.wait_window(win)
        return bool(allowed)

    def choose():
        path = filedialog.askopenfilename(title="Choose the narration JSON",
                                           initialdir=project, filetypes=[("Narration scripts", "*.json")], parent=root)
        if not path:
            return
        try:
            items, total = load_batch(Path(path))
            if not review(items, total):
                return
            key = read_key() or set_key()
            if not key:
                return
            status.set("Rendering. This can take a minute.")
            root.update_idletasks()
            out = render_batch(items, project / "Gallery voice output", key)
            status.set("Done. Nothing was published.")
            messagebox.showinfo("Gallery Voice", f"Send Astra just this file:\n\n{out.name}", parent=root)
            os.startfile(out.parent)
        except (ValueError, OSError, renderer.NarrationError, KeyError, UnicodeError) as exc:
            status.set("Render stopped. Completed clips can be reused.")
            messagebox.showerror("Gallery Voice", str(exc), parent=root)

    tk.Label(root, textvariable=status, padx=18, pady=14).pack()
    tk.Button(root, text="Choose narration file", command=choose).pack(pady=4, ipadx=12)
    tk.Button(root, text="Set or replace Google key", command=set_key).pack(pady=8)
    root.mainloop()

if __name__ == "__main__":
    gui()
