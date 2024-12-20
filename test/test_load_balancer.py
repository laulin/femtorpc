import unittest
import threading
import time

from femtorpc.tcp_daemon import TCPDaemon
from femtorpc.tcp_proxy import TCPProxy
from femtorpc.daemon import Daemon
from femtorpc.proxy import Proxy
from femtorpc.load_balancer import LoadBalancer

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
        self.join()
        
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

        

class LoadBalancerThread(threading.Thread):
    def __init__(self, load_balancer:LoadBalancer):
        super().__init__()
        self._load_balancer = load_balancer

    def run(self):
        self._load_balancer.run()


class TestLoadBalancer(unittest.TestCase):
    pass
    def test_tcp(self):
        lb = LoadBalancer("tcp://*:5555", "tcp://*:5556")
        lb_thread = LoadBalancerThread(lb)
        lb_thread.start()

        def make_foo(name):
            def foo(i):
                return name
            return foo
        

        daemon_a = TCPDaemon("127.0.0.1", 5556, "connect")
        daemon_a.register(make_foo("a"))
        daemon_b = TCPDaemon("127.0.0.1", 5556, "connect")
        daemon_b.register(make_foo("b"))

        daemon_thread_a = DaemonThread(daemon_a)
        daemon_thread_a.start()
        daemon_thread_b = DaemonThread(daemon_b)
        daemon_thread_b.start()


        with TCPProxy("127.0.0.1", 5555) as proxy:
            results = []
            for i in range(10):
                results.append(proxy.foo(i))
            print(results)

        daemon_thread_a.stop()
        daemon_thread_b.stop()

        daemon_a.close()
        daemon_b.close()

        lb.close()
        lb_thread.join()

        self.assertTrue("a" in results and "b" in results)

    def test_ipc(self):
        lb = LoadBalancer("tcp://*:5555", "ipc:///tmp/femtorpc")
        lb_thread = LoadBalancerThread(lb)
        lb_thread.start()

        def make_foo(name):
            def foo()->str:
                return name
            return foo

        daemon_a = Daemon("ipc:///tmp/femtorpc", "connect")
        daemon_a.register(make_foo("a"))
        daemon_b = Daemon("ipc:///tmp/femtorpc", "connect")
        daemon_b.register(make_foo("b"))

        daemon_thread_a = DaemonThread(daemon_a)
        daemon_thread_a.start()
        daemon_thread_b = DaemonThread(daemon_b)
        daemon_thread_b.start()


        with TCPProxy("127.0.0.1", 5555) as proxy:
            results = []
            for i in range(10):
                results.append(proxy.foo())


        daemon_thread_b.stop()
        daemon_thread_a.stop()
        
        daemon_a.close()
        daemon_b.close()

        lb.close()

        self.assertTrue("a" in results and "b" in results)