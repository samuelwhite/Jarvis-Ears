import unittest

from jarvis_ears.buffer.ring_buffer import RingBuffer


class RingBufferTests(unittest.TestCase):
    def test_ring_buffer_keeps_recent_bytes_only(self) -> None:
        buffer = RingBuffer(capacity=5)

        buffer.append(b"abc")
        buffer.append(b"def")

        self.assertEqual(buffer.size, 5)
        self.assertEqual(buffer.get_bytes(), b"bcdef")

    def test_ring_buffer_replaces_contents_when_chunk_exceeds_capacity(self) -> None:
        buffer = RingBuffer(capacity=4)

        buffer.append(b"ab")
        buffer.append(b"123456")

        self.assertEqual(buffer.size, 4)
        self.assertEqual(buffer.get_bytes(), b"3456")

    def test_ring_buffer_ignores_empty_appends(self) -> None:
        buffer = RingBuffer(capacity=3)

        buffer.append(b"")

        self.assertEqual(buffer.size, 0)
        self.assertEqual(buffer.get_bytes(), b"")

    def test_ring_buffer_rejects_non_positive_capacity(self) -> None:
        with self.assertRaises(ValueError):
            RingBuffer(capacity=0)


if __name__ == "__main__":
    unittest.main()
