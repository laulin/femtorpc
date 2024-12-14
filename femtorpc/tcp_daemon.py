import logging

import zmq
import dill

from femtorpc.command_handler import CommandHandler

class TCPDaemon:
    def __init__(self, hostname:str, port:int, loads=dill.loads, dumps=dill.dumps):
        self._command_hander = CommandHandler(loads, dumps)
        logging.getLogger(f"{self.__class__.__name__}(tcp://{hostname}:{port}")
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind(f"tcp://{hostname}:{port}")
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)

    def register(self, obj:object, name:str=None):
        self._command_hander.register(obj, name)

    def run_once(self, timeout:int=100, ignore_timeout:bool=False):
        socks = dict(self._poller.poll(timeout))
        if self._socket in socks and socks[self._socket] == zmq.POLLIN:
            request_stream = self._socket.recv()
            response_stream = self._command_hander.call(request_stream)
            self._socket.send(response_stream)
        else:
            # timeout
            if not ignore_timeout:
                raise IOError("Timeout processing request")

    def request_loop(self, timeout:int=100, condition=True):
        while condition:
            self.run_once(timeout, False)

    def close(self):
        self._context.destroy()