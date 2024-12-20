import logging

import zmq
import dill

from femtorpc.command_handler import CommandHandler

class Daemon:
    def __init__(self, adress:str, mode:str="bind", loads=dill.loads, dumps=dill.dumps, max_volatile:int=1000):
        self._command_hander = CommandHandler(loads, dumps, max_volatile)
        logging.getLogger(f"{self.__class__.__name__}({adress})")
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        if mode == "bind":
            self._socket.bind(adress)
        elif mode == "connect": 
            self._socket.connect(adress)
        else:
            raise Exception(f"mode '{mode}' is not supported")
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