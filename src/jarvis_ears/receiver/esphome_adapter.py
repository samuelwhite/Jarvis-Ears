"""Stub adapter for future direct ESPHome audio ingest."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from jarvis_ears.config import AudioConfig, DeviceConfig
from jarvis_ears.receiver.base import ReceiverReadiness


@dataclass(frozen=True, slots=True)
class ESPHomeDirectIngestCandidate:
    """A plausible transport path worth validating for direct ingest."""

    name: str
    description: str
    requires_custom_device_code: bool
    evidence_needed: tuple[str, ...]


class ESPHomeIngestStub:
    """Placeholder for a verified direct ESPHome ingest adapter.

    Known:
    - The current hardware baseline is an M5Stack Atom Echo running ESPHome.
    - The microphone pin configuration and test device host are documented.

    Unknown:
    - Which direct transport should be used for live microphone audio from this
      firmware baseline into Jarvis-Ears.
    - Whether the desired path is natively exposed by ESPHome, needs a custom
      component, or should be validated temporarily via another bridge.

    This class is intentionally honest about those gaps and should not be
    treated as a working ingest implementation yet.
    """

    def __init__(self, devices: Sequence[DeviceConfig], audio: AudioConfig) -> None:
        self._devices = list(devices)
        self._audio = audio
        self._candidates = (
            ESPHomeDirectIngestCandidate(
                name="microphone-on-data-custom-emitter",
                description=(
                    "Use ESPHome microphone capture on-device and emit raw framed audio "
                    "to Jarvis-Ears through a custom network path."
                ),
                requires_custom_device_code=True,
                evidence_needed=(
                    "A working Atom Echo firmware build that emits microphone frames off-device",
                    "Confirmed framing, sample format, and backpressure behavior",
                ),
            ),
            ESPHomeDirectIngestCandidate(
                name="native-esphome-direct-stream",
                description=(
                    "Consume a stock ESPHome transport directly from Jarvis-Ears if one exists "
                    "for microphone streaming outside Home Assistant."
                ),
                requires_custom_device_code=False,
                evidence_needed=(
                    "Official documentation or source proving a supported direct stream path",
                    "A reproducible capture session from the current Atom Echo baseline",
                ),
            ),
        )

    @property
    def name(self) -> str:
        return "esphome-direct-ingest-stub"

    def describe_readiness(self) -> ReceiverReadiness:
        candidate_names = ", ".join(candidate.name for candidate in self._candidates)
        return ReceiverReadiness(
            implemented=False,
            summary=(
                "ESPHome direct ingest is still a stub because the transport from the current "
                "Atom Echo baseline to Jarvis-Ears has not been verified."
            ),
            blockers=(
                "No confirmed stock ESPHome microphone stream that Jarvis-Ears can consume directly",
                "No verified framing contract for raw audio bytes, timing, or reconnect behavior",
            ),
            next_checks=(
                "Verify whether current ESPHome exposes any direct microphone stream outside Home Assistant",
                f"Validate one candidate path experimentally: {candidate_names}",
            ),
        )

    @property
    def candidate_paths(self) -> tuple[ESPHomeDirectIngestCandidate, ...]:
        """Return transport candidates that still need real-world verification."""

        return self._candidates

    def start(self) -> None:
        raise NotImplementedError(
            "Direct ESPHome audio ingest has not been implemented because the "
            "transport and integration details still need verification."
        )

    def stop(self) -> None:
        raise NotImplementedError(
            "There is no active ESPHome ingest session to stop in the current stub."
        )
