"""Experimental TCP audio collector for the Atom Echo custom-emitter spike.

This module is intentionally non-production. It exists only to validate whether
an ESPHome custom emitter can forward microphone bytes to Jarvis-Ears in a way
that is observable enough to design a real receiver later.
"""

from __future__ import annotations

import argparse
import logging
import socket
import time
from dataclasses import dataclass, field
from pathlib import Path


LOGGER = logging.getLogger("jarvis_ears.experiments.tcp_audio_collector")


@dataclass(slots=True)
class ChunkObservation:
    """Metadata recorded for one observed inbound chunk."""

    chunk_size: int
    offset_seconds: float
    delta_seconds: float | None


@dataclass(slots=True)
class CollectorStats:
    """In-memory summary of one collector session."""

    session_started_at: float
    total_bytes: int = 0
    total_chunks: int = 0
    largest_chunk: int = 0
    last_chunk_at: float | None = None
    observations: list[ChunkObservation] = field(default_factory=list)

    def record_chunk(self, chunk_size: int, received_at: float) -> ChunkObservation:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        delta_seconds: float | None = None
        if self.last_chunk_at is not None:
            delta_seconds = received_at - self.last_chunk_at

        observation = ChunkObservation(
            chunk_size=chunk_size,
            offset_seconds=received_at - self.session_started_at,
            delta_seconds=delta_seconds,
        )
        self.total_bytes += chunk_size
        self.total_chunks += 1
        self.largest_chunk = max(self.largest_chunk, chunk_size)
        self.last_chunk_at = received_at
        self.observations.append(observation)
        return observation

    @property
    def average_chunk_size(self) -> float:
        if self.total_chunks == 0:
            return 0.0
        return self.total_bytes / self.total_chunks

    @property
    def average_delta_seconds(self) -> float | None:
        deltas = [
            observation.delta_seconds
            for observation in self.observations
            if observation.delta_seconds is not None
        ]
        if not deltas:
            return None
        return sum(deltas) / len(deltas)

    def summary_line(self) -> str:
        average_delta = self.average_delta_seconds
        cadence_text = "unknown"
        if average_delta is not None:
            cadence_text = f"{average_delta:.4f}s avg delta"
        return (
            f"chunks={self.total_chunks} total_bytes={self.total_bytes} "
            f"largest_chunk={self.largest_chunk} avg_chunk={self.average_chunk_size:.1f} "
            f"cadence={cadence_text}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Experimental TCP collector for the Atom Echo custom-emitter spike. "
            "This is not production ingest."
        )
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind to.")
    parser.add_argument("--port", type=int, default=8765, help="TCP port to listen on.")
    parser.add_argument(
        "--recv-size",
        type=int,
        default=4096,
        help="Socket receive size per read.",
    )
    parser.add_argument(
        "--write-debug-artifact",
        action="store_true",
        help="Write received bytes to disk after the session for debugging.",
    )
    parser.add_argument(
        "--debug-output",
        type=Path,
        default=Path("experiments/last_tcp_audio_capture.bin"),
        help="Output path used only with --write-debug-artifact.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Standard library logging level.",
    )
    return parser


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def maybe_write_debug_artifact(
    enabled: bool,
    output_path: Path,
    payload: bytes,
) -> Path | None:
    """Optionally write a debug artifact only when explicitly enabled."""

    if not enabled:
        return None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(payload)
    return output_path


def finalize_session(
    stats: CollectorStats,
    payload: bytes,
    write_debug_artifact: bool,
    debug_output: Path,
) -> Path | None:
    """Log session results and optionally persist an explicit debug artifact."""

    artifact_path = maybe_write_debug_artifact(
        enabled=write_debug_artifact,
        output_path=debug_output,
        payload=payload,
    )
    LOGGER.info("Session summary: %s", stats.summary_line())
    if artifact_path is not None:
        LOGGER.info("Debug artifact written to %s", artifact_path)
    return artifact_path


def serve_forever(host: str, port: int, recv_size: int, write_debug_artifact: bool, debug_output: Path) -> int:
    """Run the collector until interrupted."""

    if port <= 0:
        raise ValueError("port must be greater than zero")
    if recv_size <= 0:
        raise ValueError("recv_size must be greater than zero")

    LOGGER.warning("Experimental spike collector starting on %s:%d", host, port)
    LOGGER.warning("This tool is for direct-ingest investigation only, not production use")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(1)

        active_stats: CollectorStats | None = None
        active_payload = bytearray()

        try:
            while True:
                LOGGER.info("Waiting for emitter connection")
                connection, address = server_socket.accept()
                with connection:
                    LOGGER.info("Emitter connected from %s:%d", address[0], address[1])
                    session_started_at = time.monotonic()
                    active_stats = CollectorStats(session_started_at=session_started_at)
                    active_payload = bytearray()

                    while True:
                        chunk = connection.recv(recv_size)
                        if not chunk:
                            LOGGER.info("Emitter disconnected")
                            break

                        received_at = time.monotonic()
                        observation = active_stats.record_chunk(len(chunk), received_at)
                        active_payload.extend(chunk)
                        delta_text = "first chunk"
                        if observation.delta_seconds is not None:
                            delta_text = f"delta={observation.delta_seconds:.4f}s"
                        LOGGER.info(
                            "Received chunk bytes=%d total_bytes=%d offset=%.4fs %s",
                            observation.chunk_size,
                            active_stats.total_bytes,
                            observation.offset_seconds,
                            delta_text,
                        )

                    finalize_session(
                        stats=active_stats,
                        payload=bytes(active_payload),
                        write_debug_artifact=write_debug_artifact,
                        debug_output=debug_output,
                    )
                    active_stats = None
                    active_payload = bytearray()
        except KeyboardInterrupt:
            LOGGER.warning("Collector interrupted by user")
            if active_stats is not None:
                finalize_session(
                    stats=active_stats,
                    payload=bytes(active_payload),
                    write_debug_artifact=write_debug_artifact,
                    debug_output=debug_output,
                )
            return 0


def main() -> int:
    args = build_parser().parse_args()
    configure_logging(args.log_level)
    return serve_forever(
        host=args.host,
        port=args.port,
        recv_size=args.recv_size,
        write_debug_artifact=args.write_debug_artifact,
        debug_output=args.debug_output,
    )


if __name__ == "__main__":
    raise SystemExit(main())
