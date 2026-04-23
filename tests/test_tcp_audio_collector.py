import shutil
import unittest
from pathlib import Path

from experiments.tcp_audio_collector import CollectorStats, maybe_write_debug_artifact


class CollectorStatsTests(unittest.TestCase):
    def test_record_chunk_tracks_counts_and_cadence(self) -> None:
        stats = CollectorStats(session_started_at=100.0)

        first = stats.record_chunk(chunk_size=320, received_at=100.05)
        second = stats.record_chunk(chunk_size=640, received_at=100.10)

        self.assertEqual(first.delta_seconds, None)
        self.assertAlmostEqual(second.delta_seconds or 0.0, 0.05, places=6)
        self.assertEqual(stats.total_chunks, 2)
        self.assertEqual(stats.total_bytes, 960)
        self.assertEqual(stats.largest_chunk, 640)
        self.assertAlmostEqual(stats.average_chunk_size, 480.0, places=6)
        self.assertAlmostEqual(stats.average_delta_seconds or 0.0, 0.05, places=6)

    def test_record_chunk_rejects_zero_size(self) -> None:
        stats = CollectorStats(session_started_at=0.0)

        with self.assertRaises(ValueError):
            stats.record_chunk(chunk_size=0, received_at=0.1)


class DebugArtifactTests(unittest.TestCase):
    def test_debug_artifact_not_written_without_flag(self) -> None:
        temp_dir = Path("tests/.tmp_collector")
        temp_dir.mkdir(exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
        output_path = temp_dir / "capture.bin"

        result = maybe_write_debug_artifact(
            enabled=False,
            output_path=output_path,
            payload=b"abc",
        )

        self.assertIsNone(result)
        self.assertFalse(output_path.exists())

    def test_debug_artifact_written_when_enabled(self) -> None:
        temp_dir = Path("tests/.tmp_collector")
        temp_dir.mkdir(exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
        output_path = temp_dir / "capture.bin"

        result = maybe_write_debug_artifact(
            enabled=True,
            output_path=output_path,
            payload=b"abc",
        )

        self.assertEqual(result, output_path)
        self.assertEqual(output_path.read_bytes(), b"abc")


if __name__ == "__main__":
    unittest.main()
