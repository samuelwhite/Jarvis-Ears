"""Downstream events emitted by Jarvis-Ears."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from jarvis_ears.stt.base import TranscriptResult


@dataclass(slots=True)
class SpeechDetected:
    device_name: str
    detected_at: datetime
    buffered_bytes: int


@dataclass(slots=True)
class TranscriptReady:
    device_name: str
    created_at: datetime
    transcript: TranscriptResult


@dataclass(slots=True)
class AudioDropped:
    device_name: str
    dropped_at: datetime
    dropped_bytes: int
    reason: str
