import logging

class ProxifyRemoteCallable:
    def __init__(self, proxy, name:str):
        self._proxy = proxy
        self._name = name
        logging.getLogger(f"{self.__class__.__name__}({name})@{self}")
        self._proxy.add_volatile(name)

    def __call__(self, *args, **kwargs):
        return self._proxy.handler.call(self._name, *args, **kwargs)