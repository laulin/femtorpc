import logging

import zmq

class LoadBalancer:
    def __init__(self, router_adress:str, dealer_adress:str):
        self._log = logging.getLogger(f"{self.__class__.__name__} {router_adress} -> {dealer_adress}")
        self._context = zmq.Context()

        # Frontend: Client connections (ROUTER socket)
        self._router = self._context.socket(zmq.ROUTER)
        self._router.bind(router_adress)  

        # Backend: Server connections (DEALER socket)
        self._dealer = self._context.socket(zmq.DEALER)
        self._dealer.bind(dealer_adress)
    
    def run(self):
        try:
            zmq.proxy(self._router, self._dealer)
        except zmq.ContextTerminated:
            self._router.close()
            self._dealer.close()
           

    def close(self):
        self._context.term()  