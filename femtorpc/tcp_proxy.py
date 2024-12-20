from femtorpc.proxy import Proxy

import dill


class TCPProxy(Proxy):
    def __init__(self, hostname:str, port:int, timeout:int=1000, loads=dill.loads, dumps=dill.dumps, public:dict=None):
        super().__init__(f"tcp://{hostname}:{port}", timeout, loads, dumps, public)
