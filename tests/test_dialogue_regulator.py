import re
from scripts.dialogue_regulator import normalize_reply


def _count_sentences(text: str) -> int:
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


def test_truncates_to_max_sentences():
    text = "One. Two. Three. Four."
    out = normalize_reply(text, {})
    assert _count_sentences(out) == 3


def test_splits_long_sentences():
    long_sentence = " ".join(["word"] * 40) + "."
    out = normalize_reply(long_sentence, {})
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", out.strip()) if s]
    assert all(len(s.split()) <= 15 for s in sentences)
