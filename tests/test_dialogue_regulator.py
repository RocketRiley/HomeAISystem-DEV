from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "scripts"))

from dialogue_regulator import normalize_reply
from emotion.orchestrator import PAD


def test_normalize_reply_trims_and_splits():
    long_text = (
        "This is the first sentence. "
        "This second sentence is intentionally made very long so that it exceeds the character limit "
        "and needs to be truncated accordingly. "
        "A third sentence should be removed entirely."
    )
    result = normalize_reply(long_text, max_chars=120, max_sentences=2)
    assert len(result) <= 120
    assert result.count(".") <= 2
    assert "third sentence" not in result.lower()


def test_normalize_reply_single_word():
    assert normalize_reply("Hello") == "Hello"


def test_normalize_reply_high_arousal_exclaimed_and_clamped():
    pad = PAD(pleasure=0.0, arousal=1.0, dominance=0.0)
    text = (
        "This news is incredibly exciting and I simply cannot contain my enthusiasm about how wonderful "
        "everything is right now."
    )
    result = normalize_reply(text, pad=pad, max_chars=80)
    assert result.endswith("!")
    assert len(result) <= 80
