import base64
from contextlib import contextmanager
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import urllib.error

import gallery_narration as n

# A structural fixture only; real playback is tested against decoded MP3s separately.
FAKE = b"\xff\xfb\x90\x64" + bytes(1400)

class NarrationTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.path = self.root / "script.json"
        self.s = {"schema": 1, "label": "Exact Gallery label", "image_id": "m74_test",
                  "captured": "2026-11", "status": "approved",
                  "spoken_script": {"intro": "Introduction", "discoverer": "Discovery",
                                    "science": "One full Moon.", "scope": "I took it in November 2026."}}
        self.write()
        self.calls = []

    def write(self):
        self.path.write_text(json.dumps(self.s), encoding="utf-8")

    def fake(self, key, config):
        self.calls.append(config)
        return FAKE

    def run_mode(self, mode, **kwargs):
        args = {"mode": mode, "key": "test-only", "fetch": self.fake}
        args.update(kwargs)
        return n.process(self.path, self.root, **args)

    def test_offline_plan_and_fixed_parts(self):
        out, _, count = self.run_mode("plan", key=None)
        rec = json.loads((out / "plan.json").read_text())["narration"]
        self.assertEqual([p["show"] for p in rec["parts"]], ["constellation", "discoverer", "moon", "scope"])
        self.assertEqual(rec["parts"][2]["hold_s"], 4)
        self.assertEqual(rec["parts"][-1]["file"], "audio/m74_test_04_scope.mp3")
        self.assertEqual(count, 0)
        self.assertFalse(self.calls)

    def test_draft_sample_then_approved_full_render_reuses_intro(self):
        self.s["status"] = "draft"
        self.write()
        out, _, count = self.run_mode("sample")
        self.assertEqual(count, 1)
        self.assertFalse((out / "gallery-record.json").exists())
        with self.assertRaises(n.NarrationError):
            self.run_mode("render")
        self.s["status"] = "approved"
        self.write()
        _, _, count = self.run_mode("render")
        self.assertEqual(count, 3)
        self.assertEqual(len(list(out.glob("*.mp3"))), 4)
        self.assertEqual(self.calls[0]["audioConfig"]["speakingRate"], 0.9)
        self.assertEqual(self.calls[0]["voice"]["name"], n.VOICE)
        self.assertTrue((out / "gallery-record.json").exists())
        self.assertEqual(self.run_mode("render")[2], 0)
        self.assertEqual(len(self.calls), 4)

    def test_interrupt_resume_and_invalid_response(self):
        def fail_after_first(key, config):
            if self.calls:
                return b"<html>not audio</html>"
            return self.fake(key, config)
        with self.assertRaises(n.NarrationError):
            self.run_mode("render", fetch=fail_after_first)
        self.assertEqual(self.run_mode("render")[2], 3)

    def test_file_conflict_refuses_overwrite(self):
        out, _, _ = self.run_mode("sample")
        p = out / "m74_test_01_intro.mp3"
        p.write_bytes(b"altered")
        with self.assertRaises(n.NarrationError):
            self.run_mode("render")
        self.assertEqual(p.read_bytes(), b"altered")
        self.assertEqual(len(self.calls), 1)

    def test_no_key_budget_and_lock(self):
        for options in [{"key": None}, {"max_chars": 1}]:
            with self.assertRaises(n.NarrationError):
                self.run_mode("sample", **options)
        out, _, _ = self.run_mode("plan")
        with n.render_lock(out), self.assertRaises(n.NarrationError):
            self.run_mode("sample")
        self.assertFalse(self.calls)

    def test_bad_identifiers_or_capture_date(self):
        for override in [{"image_id": "../bad"}, {"captured": "2026-11-07"},
                         {"spoken_script": {**self.s["spoken_script"], "scope": "Nov 2026."}},
                         {"spoken_script": {**self.s["spoken_script"], "scope": "In November 2026, on 4 November."}}]:
            with self.subTest(override=override), patch.dict(self.s, override):
                self.write()
                with self.assertRaises(n.NarrationError):
                    n.load_script(self.path)

    def test_google_request_uses_header_and_errors_dont_echo_key(self):
        observed = []
        class Mock:
            @contextmanager
            def open(self, req, timeout):
                observed.append((req, timeout))
                class Response:
                    def read(self, cap):
                        return json.dumps({"audioContent": base64.b64encode(FAKE).decode()}).encode()
                yield Response()
        config = n.plan(self.s)[0][0][1]
        with patch.object(n.urllib.request, "build_opener", return_value=Mock()):
            self.assertEqual(n.synthesize("test-key", config), FAKE)
        req, _ = observed[0]
        self.assertEqual(req.full_url, n.ENDPOINT)
        self.assertEqual(req.get_header("X-goog-api-key"), "test-key")
        with patch.object(n.urllib.request.OpenerDirector, "open", side_effect=urllib.error.HTTPError(n.ENDPOINT, 403, "test-key", {}, None)):
            with self.assertRaises(n.NarrationError) as err:
                n.synthesize("test-key", config)
        self.assertIn("403", str(err.exception))
        self.assertNotIn("test-key", str(err.exception))

if __name__ == "__main__":
    unittest.main()
