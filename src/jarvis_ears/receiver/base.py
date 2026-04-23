"""Base interfaces for device audio receivers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


@dataclass(slots=True)
class AudioChunk:
    """A chunk of audio captured from a device."""

    device_name: str
    data: bytes
    received_at: datetime
    sample_rate_hz: int
    channels: int
    sample_width_bytes: int


@dataclass(slots=True)
class ReceiverReadiness:
    """Developer-facing description of receiver implementation status."""

    implemented: bool
    summary: str
    blockers: tuple[str, ...] = field(default_factory=tuple)
    next_checks: tuple[str, ...] = field(default_factory=tuple)


class AudioReceiver(Protocol):
    """Interface for receiver implementations."""

    @property
    def name(self) -> str:
        """Return a human-readable receiver name."""

    def describe_readiness(self) -> ReceiverReadiness:
        """Describe whether this receiver is ready for real ingest."""

    def start(self) -> None:
        """Start the receiver."""

    def stop(self) -> None:
        """Stop the receiver."""
