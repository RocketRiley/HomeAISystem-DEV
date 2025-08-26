from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts"))
from prompt_manager import build_messages

def test_human_mode_prompt():
    msgs = build_messages("hello", human_mode=True)
    assert "never disclose" in msgs[0]["content"].lower()
    msgs2 = build_messages("hello", human_mode=False)
    assert "may mention" in msgs2[0]["content"].lower()
