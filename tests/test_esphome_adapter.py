import unittest

from jarvis_ears.config import AudioConfig, DeviceConfig
from jarvis_ears.receiver.esphome_adapter import ESPHomeIngestStub


class ESPHomeAdapterTests(unittest.TestCase):
    def test_stub_reports_not_ready_and_lists_candidates(self) -> None:
        adapter = ESPHomeIngestStub(
            devices=[
                DeviceConfig(
                    name="atom-echo-test",
                    room="kitchen",
                    host="192.168.5.236",
                )
            ],
            audio=AudioConfig(
                sample_rate_hz=16000,
                ring_buffer_bytes=64000,
                chunk_bytes_hint=2048,
            ),
        )

        readiness = adapter.describe_readiness()

        self.assertFalse(readiness.implemented)
        self.assertIn("not been verified", readiness.summary)
        self.assertEqual(len(adapter.candidate_paths), 2)
        self.assertEqual(adapter.candidate_paths[0].name, "microphone-on-data-custom-emitter")


if __name__ == "__main__":
    unittest.main()
