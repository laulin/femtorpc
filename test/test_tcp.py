import unittest
import threading

from femtorpc.tcp_daemon import TCPDaemon
from femtorpc.tcp_proxy import TCPProxy

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


class TestTCP(unittest.TestCase):
    def test_callable(self):

        daemon = TCPDaemon("127.0.0.1", 6666)
        def foo(x)->int:
            return x + 1
        
        daemon.register(foo, "foo")
        with DaemonThread(daemon) as thread:

            proxy = TCPProxy("127.0.0.1", 6666, 100)

            result = proxy.foo(1)

            self.assertEqual(result, 2)

        daemon.close()
        proxy.close()

    def test_callable_with_context(self):

        daemon = TCPDaemon("127.0.0.1", 6666)
        def foo(x)->int:
            return x + 1
        
        daemon.register(foo, "foo")
        with DaemonThread(daemon) as thread:

            with TCPProxy("127.0.0.1", 6666, 100) as proxy:
                result = proxy.foo(1)
                self.assertEqual(result, 2)

        daemon.close()


    def test_closure(self):

        daemon = TCPDaemon("127.0.0.1", 6666)
        def foo(x):
            def bar(y)->int:
                return x + y
            return bar
        
        daemon.register(foo, "foo")
        with DaemonThread(daemon) as thread:

            with TCPProxy("127.0.0.1", 6666, 100) as proxy:

                bar = proxy.foo(1)
                result = bar(2)

                self.assertEqual(result, 3)


        daemon.close()

    def test_generator(self):

        daemon = TCPDaemon("127.0.0.1", 6666)
        def foo():
            for i in range(3):
                yield i
        
        daemon.register(foo, "foo")
        with DaemonThread(daemon) as thread:
            with TCPProxy("127.0.0.1", 6666, 100) as proxy:
                result = [i for i in proxy.foo()]
                self.assertListEqual(result, [0,1,2])

        daemon.close()

    def test_object(self):

        daemon = TCPDaemon("127.0.0.1", 6666)
        class foo():
            def bar(self)->int:
                return 666
        
        myfoo = foo()
        daemon.register(myfoo, "foo")
        with DaemonThread(daemon) as thread:
            with TCPProxy("127.0.0.1", 6666, 100) as proxy:
                result = proxy.foo.bar()
                self.assertEqual(result, 666)

        daemon.close()

    def test_big_payload(self):
        # send 10Mb of data
        daemon = TCPDaemon("127.0.0.1", 6666)
        def foo(x:bytes)->int:
            return len(x)
        
        daemon.register(foo, "foo")
        SIZE = 1024*1024*10
        data = b"0"*SIZE
        with DaemonThread(daemon) as thread:
            with TCPProxy("127.0.0.1", 6666, 200) as proxy:
                result = proxy.foo(data)
                self.assertEqual(result, SIZE)

        daemon.close()