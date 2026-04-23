"""Base STT interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class TranscriptResult:
    """Transcript output produced by an STT engine."""

    text: str
    confidence: float | None = None
    language: str | None = None


class SpeechToTextEngine(Protocol):
    """Interface for future STT implementations."""

    def transcribe(self, audio_bytes: bytes) -> TranscriptResult:
        """Transcribe audio bytes into text."""
