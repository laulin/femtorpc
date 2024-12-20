import dill

from femtorpc.daemon import Daemon

class TCPDaemon(Daemon):
    def __init__(self, hostname:str, port:int, mode:str="bind", loads=dill.loads, dumps=dill.dumps, max_volatile:int=1000):
        super().__init__(f"tcp://{hostname}:{port}", mode, loads, dumps, max_volatile)