from femtorpc.proxy_wrapper import ProxyWrapper
from femtorpc.response import Response

import dill
import zmq

class TCPProxy(ProxyWrapper):
    def __init__(self, hostname:str, port:int, timeout:int=1000, loads=dill.loads, dumps=dill.dumps):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect(f"tcp://{hostname}:{port}")
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)
        self._timeout = timeout
        super().__init__(self._callback, loads, dumps)

    def _callback(self, datastream:bytes)->bytes:
        self._socket.send(datastream)
        socks = dict(self._poller.poll(self._timeout))

        if self._socket in socks and socks[self._socket] == zmq.POLLIN:
            return self._socket.recv()
        else:
            raise IOError("Timeout processing request")
        
    def close(self):
        self._context.destroy()
