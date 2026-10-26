"""Shared test helpers: a fake claude command and sample answers."""

import io
import json
import os
import stat
import sys
from pathlib import Path

from PIL import Image

FAKE_CLAUDE = '''
import json, os, sys
prompt = sys.stdin.read()
record = {"argv": sys.argv[1:], "cwd": os.getcwd(), "prompt": prompt, "files": sorted(os.listdir("."))}
with open(os.environ["FAKE_RECORD"], "w") as f:
    json.dump(record, f)
print(json.dumps({"type": "result", "is_error": False, "result": os.environ["FAKE_ANSWER"]}))
'''

BANANA = {
    "is_produce": True, "produce_type": "fruit", "name": "Banana", "freshness_score": 72,
    "ready_to_eat": "yes", "days_left": 2, "storage_tip": "Keep at room temperature.",
    "confidence": 88, "description": "Mostly yellow with a few brown spots.",
}
CAT = {
    "is_produce": False, "produce_type": None, "name": None, "freshness_score": None,
    "ready_to_eat": None, "days_left": None, "storage_tip": None, "confidence": 95,
    "description": "a cat",
}


def envelope(answer) -> str:
    text = answer if isinstance(answer, str) else json.dumps(answer)
    return json.dumps({"type": "result", "is_error": False, "result": text})


def make_fake_claude(folder: Path, answer: dict, record: Path) -> str:
    script = folder / "fake_claude"
    script.write_text(f"#!{sys.executable}\n{FAKE_CLAUDE}")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    os.environ["FAKE_ANSWER"] = json.dumps(answer)
    os.environ["FAKE_RECORD"] = str(record)
    return str(script)


def jpeg_bytes(color="yellow", size=(40, 30)) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", size, color).save(output, "JPEG")
    return output.getvalue()
