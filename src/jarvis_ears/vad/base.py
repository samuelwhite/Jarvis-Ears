"""Base VAD interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from jarvis_ears.receiver.base import AudioChunk


@dataclass(slots=True)
class VoiceActivityResult:
    """Result from a VAD stage."""

    speech_detected: bool
    confidence: float | None = None


class VoiceActivityDetector(Protocol):
    """Interface for future VAD implementations."""

    def evaluate(self, chunk: AudioChunk) -> VoiceActivityResult:
        """Evaluate an audio chunk for speech."""
