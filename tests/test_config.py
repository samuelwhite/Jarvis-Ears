import shutil
import unittest
from pathlib import Path

from jarvis_ears.config import load_config


class ConfigLoadingTests(unittest.TestCase):
    def test_load_config_reads_example_json(self) -> None:
        config = load_config(Path("config.example.json"))

        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.audio.sample_rate_hz, 16000)
        self.assertEqual(config.audio.ring_buffer_bytes, 64000)
        self.assertEqual(len(config.devices), 1)
        self.assertEqual(config.devices[0].name, "atom-echo-test")
        self.assertEqual(config.devices[0].host, "192.168.5.236")

    def test_load_config_rejects_unknown_fields(self) -> None:
        temp_dir = Path("tests/.tmp_config")
        temp_dir.mkdir(exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
        config_path = temp_dir / "config.json"
        config_path.write_text(
            (
                "{"
                '"log_level": "INFO",'
                '"audio": {'
                '"sample_rate_hz": 16000,'
                '"sample_width_bytes": 2,'
                '"channels": 1,'
                '"ring_buffer_bytes": 32000,'
                '"chunk_bytes_hint": 2048'
                "},"
                '"devices": [],'
                '"unexpected": true'
                "}"
            ),
            encoding="utf-8",
        )

        with self.assertRaises(Exception) as context:
            load_config(config_path)

        self.assertIn("unexpected", str(context.exception))


if __name__ == "__main__":
    unittest.main()
