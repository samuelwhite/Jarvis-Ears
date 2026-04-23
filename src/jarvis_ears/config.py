"""Configuration models and loading helpers for Jarvis-Ears."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when configuration validation fails."""


def _expect_keys(section: str, data: dict[str, Any], allowed: set[str]) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise ConfigError(f"{section} contains unknown field(s): {sorted(unknown)}")


def _require_int(section: str, field_name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ConfigError(f"{section}.{field_name} must be a positive integer")
    return value


def _require_str(section: str, field_name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{section}.{field_name} must be a non-empty string")
    return value


@dataclass(slots=True)
class DeviceConfig:
    """Configuration for an audio source device."""

    name: str
    room: str
    host: str
    firmware: str = "esphome"
    receiver: str = "esphome"
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceConfig":
        _expect_keys(
            "devices[]",
            data,
            {"name", "room", "host", "firmware", "receiver", "enabled"},
        )
        enabled = data.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ConfigError("devices[].enabled must be a boolean")
        return cls(
            name=_require_str("devices[]", "name", data.get("name")),
            room=_require_str("devices[]", "room", data.get("room")),
            host=_require_str("devices[]", "host", data.get("host")),
            firmware=_require_str("devices[]", "firmware", data.get("firmware", "esphome")),
            receiver=_require_str("devices[]", "receiver", data.get("receiver", "esphome")),
            enabled=enabled,
        )


@dataclass(slots=True)
class AudioConfig:
    """Audio pipeline configuration."""

    sample_rate_hz: int
    ring_buffer_bytes: int
    chunk_bytes_hint: int
    sample_width_bytes: int = 2
    channels: int = 1

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AudioConfig":
        _expect_keys(
            "audio",
            data,
            {
                "sample_rate_hz",
                "sample_width_bytes",
                "channels",
                "ring_buffer_bytes",
                "chunk_bytes_hint",
            },
        )
        return cls(
            sample_rate_hz=_require_int("audio", "sample_rate_hz", data.get("sample_rate_hz")),
            sample_width_bytes=_require_int(
                "audio", "sample_width_bytes", data.get("sample_width_bytes", 2)
            ),
            channels=_require_int("audio", "channels", data.get("channels", 1)),
            ring_buffer_bytes=_require_int(
                "audio", "ring_buffer_bytes", data.get("ring_buffer_bytes")
            ),
            chunk_bytes_hint=_require_int(
                "audio", "chunk_bytes_hint", data.get("chunk_bytes_hint")
            ),
        )


@dataclass(slots=True)
class AppConfig:
    """Top-level application configuration."""

    audio: AudioConfig
    devices: list[DeviceConfig] = field(default_factory=list)
    log_level: str = "INFO"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        _expect_keys("root", data, {"log_level", "audio", "devices"})

        log_level = data.get("log_level", "INFO")
        if not isinstance(log_level, str) or not log_level.strip():
            raise ConfigError("root.log_level must be a non-empty string")

        raw_audio = data.get("audio")
        if not isinstance(raw_audio, dict):
            raise ConfigError("root.audio must be an object")

        raw_devices = data.get("devices", [])
        if not isinstance(raw_devices, list):
            raise ConfigError("root.devices must be a list")

        devices: list[DeviceConfig] = []
        for item in raw_devices:
            if not isinstance(item, dict):
                raise ConfigError("root.devices entries must be objects")
            devices.append(DeviceConfig.from_dict(item))

        return cls(
            log_level=log_level,
            audio=AudioConfig.from_dict(raw_audio),
            devices=devices,
        )


def load_config(path: str | Path) -> AppConfig:
    """Load application configuration from a JSON file."""

    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        raw_config = json.load(handle)
    if not isinstance(raw_config, dict):
        raise ConfigError("root config must be a JSON object")
    return AppConfig.from_dict(raw_config)
