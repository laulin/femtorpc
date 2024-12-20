from multiprocessing import Process, Event
import threading
import time

from femtorpc.daemon import Daemon
from femtorpc.load_balancer import LoadBalancer

LOAD_BALANCER_INPUT = "tcp://127.0.0.1:6666"
LOAD_BALANCER_OUTPUT = "ipc:///tmp/scalable"
NUMBER_OF_PROCESS = 4


class DaemonProcess(Process):
    # Real process used to menage each RPC daemon
    def __init__(self, daemon_id):
        super().__init__()
        self.running = Event()
        self.running.set()
        self._daemon = None
        self._daemon_id = daemon_id

    def run(self):
        # each daemon return daemon_x on foo() call
        def foo():
            return f"Daemon_{self._daemon_id}"
        
        self._daemon = Daemon(LOAD_BALANCER_OUTPUT, mode="connect")
        self._daemon.register(foo)
        try:
            while self.running.is_set():
                self._daemon.run_once(10, True)
        except KeyboardInterrupt:
            pass
        finally:
            self._daemon.close()

    def stop(self):
        self.running.clear()
        self.join()

class LoadBalancerThread(threading.Thread):
    # We use a simple thread for the load balancer
    def __init__(self, load_balancer:LoadBalancer):
        super().__init__()
        self._load_balancer = load_balancer

    def run(self):
        self._load_balancer.run()
        

if __name__ == "__main__":
    # starting the entry point of the RPC server
    lb = LoadBalancer(LOAD_BALANCER_INPUT, LOAD_BALANCER_OUTPUT)
    lb_thread = LoadBalancerThread(lb)
    lb_thread.start()
    
    # creating daemons
    daemons = []
    for i in range(NUMBER_OF_PROCESS):
        
        daemon_process = DaemonProcess(i)
        daemon_process.start()
        daemons.append(daemon_process)

    # wait loop
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # cleaning
        for daemon_process in daemons:
            daemon_process.stop()

        lb.close()
        lb_thread.join()