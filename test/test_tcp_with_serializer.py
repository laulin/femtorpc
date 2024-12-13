import unittest
import threading

from femtorpc.tcp_daemon import TCPDaemon
from femtorpc.tcp_proxy import TCPProxy
from femtorpc.serializer import get_serializer

class DaemonThread(threading.Thread):
    def __init__(self, daemon:TCPDaemon):
        super().__init__()
        self.running = threading.Event()
        self.running.set()  # Indique que le thread est actif
        self._daemon = daemon

    def run(self):
        while self.running.is_set():
            self._daemon.run_once(10, True)

    def stop(self):
        self.running.clear()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.join()

KEY = b"00000000000000000000000000000000"

class TestTCPWithSeriliazer(unittest.TestCase):
    def test_nothing(self):

        daemon = TCPDaemon("127.0.0.1", 6666, **get_serializer())
        def foo(x)->int:
            return x + 1
        
        daemon.register("foo", foo)
        with DaemonThread(daemon) as thread:

            proxy = TCPProxy("127.0.0.1", 6666, 100)

            result = proxy.foo(1)

            self.assertEqual(result, 2)

        daemon.close()
        proxy.close()

    def test_compression(self):

        daemon = TCPDaemon("127.0.0.1", 6666, **get_serializer(compressed=True))
        def foo(x)->int:
            return x + 1
        
        daemon.register("foo", foo)
        with DaemonThread(daemon) as thread:

            proxy = TCPProxy("127.0.0.1", 6666, 100, **get_serializer(compressed=True))

            result = proxy.foo(1)

            self.assertEqual(result, 2)

        daemon.close()
        proxy.close()

    def test_encryption(self):

        daemon = TCPDaemon("127.0.0.1", 6666, **get_serializer(key=KEY))
        def foo(x)->int:
            return x + 1
        
        daemon.register("foo", foo)
        with DaemonThread(daemon) as thread:

            with TCPProxy("127.0.0.1", 6666, 100, **get_serializer(key=KEY)) as proxy:
                result = proxy.foo(1)
                self.assertEqual(result, 2)

        daemon.close()
        proxy.close()

    def test_encryption_and_compression(self):

        daemon = TCPDaemon("127.0.0.1", 6666, **get_serializer(key=KEY, compressed=True))
        def foo(x)->int:
            return x + 1
        
        daemon.register("foo", foo)
        with DaemonThread(daemon) as thread:

            with TCPProxy("127.0.0.1", 6666, 100, **get_serializer(key=KEY, compressed=True)) as proxy:
                result = proxy.foo(1)
                self.assertEqual(result, 2)

        daemon.close()
        proxy.close()

    