"""Minimal startup path for Jarvis-Ears."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from jarvis_ears.buffer.ring_buffer import RingBuffer
from jarvis_ears.config import load_config
from jarvis_ears.logging import configure_logging
from jarvis_ears.receiver.esphome_adapter import ESPHomeIngestStub


LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Jarvis-Ears")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.json"),
        help="Path to a Jarvis-Ears JSON config file.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_config(args.config)
    configure_logging(config.log_level)

    receiver = ESPHomeIngestStub(devices=config.devices, audio=config.audio)
    ring_buffer = RingBuffer(capacity=config.audio.ring_buffer_bytes)
    readiness = receiver.describe_readiness()

    LOGGER.info(
        "Jarvis-Ears started with %d device(s), receiver=%s, ring_buffer_bytes=%d",
        len(config.devices),
        receiver.name,
        ring_buffer.capacity,
    )
    LOGGER.info("Receiver readiness: implemented=%s summary=%s", readiness.implemented, readiness.summary)
    for blocker in readiness.blockers:
        LOGGER.info("Receiver blocker: %s", blocker)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
