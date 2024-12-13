import logging

from femtorpc.proxify_remote_callable import ProxifyRemoteCallable
from femtorpc.proxify_remote_generator import ProxifyRemoteGenerator
from femtorpc.response import Function, Generator

class ProxifyCallable:
    def __init__(self, proxy, name:str):
        self._proxy = proxy
        self._name = name
        logging.getLogger(f"{self.__class__.__name__}({name})@{self}")


    def __call__(self, *args, **kwargs):
        return_value = self._proxy.handler.call(self._name, *args, **kwargs)

        if isinstance(return_value, Function):
            return ProxifyRemoteCallable(self._proxy, return_value.id)
        
        if isinstance(return_value, Generator):
            return ProxifyRemoteGenerator(self._proxy, return_value.id)
        
        return return_value