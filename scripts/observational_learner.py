from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import subprocess
import tempfile

from .skill_acquisition import SkillAcquisitionManager
from .llm_adapter import generate_response

class ObservationalLearner:
    """Learn new skills by observing instructional videos."""

    def __init__(self, skills: SkillAcquisitionManager) -> None:
        self.skills = skills

    def ingest_video(self, url: str) -> Tuple[Path, Path]:
        """Download video and audio streams via yt-dlp."""
        tmpdir = Path(tempfile.mkdtemp())
        video_path = tmpdir / "video.mp4"
        audio_path = tmpdir / "audio.mp3"
        cmd = [
            "yt-dlp",
            "-f",
            "best",
            "-o",
            str(video_path),
            url,
        ]
        subprocess.run(cmd, check=False)
        # Extract audio
        subprocess.run(["ffmpeg", "-y", "-i", str(video_path), str(audio_path)], check=False)
        return video_path, audio_path

    def process_senses(self, video_file: Path, audio_file: Path) -> Tuple[str, List[str]]:
        """Transcribe audio and perform simple video analysis."""
        transcript = ""
        try:
            from faster_whisper import WhisperModel

            model = WhisperModel("small")
            segments, _ = model.transcribe(str(audio_file))
            transcript = " ".join([s.text for s in segments])
        except Exception:
            pass

        # Placeholder for CV analysis
        frames: List[str] = []
        try:
            import cv2

            cap = cv2.VideoCapture(str(video_file))
            ret, frame = cap.read()
            if ret:
                frames.append("frame_captured")
            cap.release()
        except Exception:
            pass
        return transcript, frames

    def synthesize_understanding(self, transcript: str, video_analysis: List[str]) -> List[str]:
        """Combine text and visuals into ordered steps."""
        prompt = (
            "Given the following transcript and visual cues, list the key steps "
            "shown in the tutorial. Return each step as a bullet point.\n\n"
            f"Transcript:\n{transcript}\nVisuals:{video_analysis}"
        )
        steps_text = generate_response(prompt, history=None, human_mode=False) or ""
        return [s.strip("- ") for s in steps_text.splitlines() if s.strip()]

    def generate_skill_from_observation(self, steps: List[str]) -> Path:
        """Create a skill from observed steps via SkillAcquisitionManager."""
        goal = "\n".join(steps)
        return self.skills.propose_skill(f"Implement the following steps:\n{goal}")
