from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts"))
from emotion_style import style_from_pad

def test_style_from_pad_blend():
    pad = {"P": 0.2, "A": 0.3, "D": 0.0}
    style = style_from_pad(pad)
    assert 0.5 <= style["temperature"] <= 1.0
    assert 0.7 <= style["top_p"] <= 0.95
    assert isinstance(style["interjection"], str)
