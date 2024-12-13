import unittest
import threading
import time

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


class Benchmark(unittest.TestCase):
    def test_number_of_request_per_second(self):
        daemon = TCPDaemon("127.0.0.1", 6666)
        def foo(x)->int:
            return x + 1
        
        daemon.register("foo", foo)
        with DaemonThread(daemon) as thread:

            with TCPProxy("127.0.0.1", 6666, 100) as proxy:

                t1 = time.time()
                for i in range(2000):
                    proxy.foo(1)

                deltat = time.time() - t1

        print(f"Native : {2000/deltat} request per second")
            

        daemon.close()

    def test_number_of_bytes_per_second(self):
        daemon = TCPDaemon("127.0.0.1", 6666)
        def foo(x)->int:
            return len(x)
        
        payload = b"0"*1024*1024*10 # 10MB
        daemon.register("foo", foo)
        with DaemonThread(daemon) as thread:

            with TCPProxy("127.0.0.1", 6666, 100) as proxy:

                t1 = time.time()
                for i in range(100):
                    proxy.foo(payload)

                deltat = time.time() - t1

        print(f"Native : {100*len(payload)/deltat} bytes per second ({100*len(payload)/(deltat*1024*1024)} Mbytes per second)")
            

        daemon.close()

    def test_number_of_request_per_second_with_compression(self):
        serial_params = get_serializer(compressed=True)
        daemon = TCPDaemon("127.0.0.1", 6666, **serial_params)
        def foo(x)->int:
            return x + 1
        
        daemon.register("foo", foo)
        with DaemonThread(daemon) as thread:

            with TCPProxy("127.0.0.1", 6666, 100, **serial_params) as proxy:

                t1 = time.time()
                for i in range(2000):
                    proxy.foo(1)

                deltat = time.time() - t1

        print(f"Compressed : {2000/deltat} request per second")
            

        daemon.close()

    def test_number_of_bytes_per_second_with_compression(self):
        serial_params = get_serializer(compressed=True)
        daemon = TCPDaemon("127.0.0.1", 6666, **serial_params)
        def foo(x)->int:
            return len(x)
        
        payload = b"0"*1024*1024*10 # 10MB
        daemon.register("foo", foo)
        with DaemonThread(daemon) as thread:

            with TCPProxy("127.0.0.1", 6666, 100, **serial_params) as proxy:

                t1 = time.time()
                for i in range(100):
                    proxy.foo(payload)

                deltat = time.time() - t1

        print(f"Compressed : {100*len(payload)/deltat} bytes per second ({100*len(payload)/(deltat*1024*1024)} Mbytes per second)")
            

        daemon.close()

    def test_number_of_request_per_second_encrypted(self):
        serial_params = get_serializer(key=KEY)
        daemon = TCPDaemon("127.0.0.1", 6666, **serial_params)
        def foo(x)->int:
            return x + 1
        
        daemon.register("foo", foo)
        with DaemonThread(daemon) as thread:

            with TCPProxy("127.0.0.1", 6666, 100, **serial_params) as proxy:

                t1 = time.time()
                for i in range(2000):
                    proxy.foo(1)

                deltat = time.time() - t1

        print(f"Encrypted : {2000/deltat} request per second")
            

        daemon.close()

    def test_number_of_bytes_per_second_encrypted(self):
        serial_params = get_serializer(key=KEY)
        daemon = TCPDaemon("127.0.0.1", 6666, **serial_params)
        def foo(x)->int:
            return len(x)
        
        payload = b"0"*1024*1024*10 # 10MB
        daemon.register("foo", foo)
        with DaemonThread(daemon) as thread:

            with TCPProxy("127.0.0.1", 6666, 1000, **serial_params) as proxy:

                t1 = time.time()
                for i in range(100):
                    proxy.foo(payload)

                deltat = time.time() - t1

        print(f"Encrypted : {100*len(payload)/deltat} bytes per second ({100*len(payload)/(deltat*1024*1024)} Mbytes per second)")
            

        daemon.close()

    def test_number_of_request_per_second_encrypted_with_compression(self):
        serial_params = get_serializer(key=KEY, compressed=True)
        daemon = TCPDaemon("127.0.0.1", 6666, **serial_params)
        def foo(x)->int:
            return x + 1
        
        daemon.register("foo", foo)
        with DaemonThread(daemon) as thread:

            with TCPProxy("127.0.0.1", 6666, 100, **serial_params) as proxy:

                t1 = time.time()
                for i in range(2000):
                    proxy.foo(1)

                deltat = time.time() - t1

        print(f"Compressed then Encrypted : {2000/deltat} request per second")
            

        daemon.close()

    def test_number_of_bytes_per_second_encrypted_with_compression(self):
        serial_params = get_serializer(key=KEY, compressed=True)
        daemon = TCPDaemon("127.0.0.1", 6666, **serial_params)
        def foo(x)->int:
            return len(x)
        
        payload = b"0"*1024*1024*10 # 10MB
        daemon.register("foo", foo)
        with DaemonThread(daemon) as thread:

            with TCPProxy("127.0.0.1", 6666, 1000, **serial_params) as proxy:

                t1 = time.time()
                for i in range(100):
                    proxy.foo(payload)

                deltat = time.time() - t1

        print(f"Compressed then Encrypted : {100*len(payload)/deltat} bytes per second ({100*len(payload)/(deltat*1024*1024)} Mbytes per second)")
            

        daemon.close()
