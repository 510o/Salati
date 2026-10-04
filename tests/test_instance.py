import socket
import unittest

from src.instance import acquire_instance_lock


class Lock(unittest.TestCase):
    def test_second_holder_is_refused_until_the_first_releases(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        first = acquire_instance_lock(port)
        self.assertIsNotNone(first)
        self.assertIsNone(acquire_instance_lock(port))   # used to succeed on Windows (SO_REUSEADDR)
        first.close()
        again = acquire_instance_lock(port)
        self.assertIsNotNone(again)
        again.close()


if __name__ == "__main__":
    unittest.main()
