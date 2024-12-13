import logging

import dill

from femtorpc.proxy_handler import ProxyHandler
from femtorpc.proxify_callable import ProxifyCallable
from femtorpc.proxify_object import ProxifyObject

class ProxyWrapper:
    def __init__(self, callback, loads=dill.loads, dumps=dill.dumps):
        self._proxy_hander = ProxyHandler(callback, loads, dumps)
        self._log = logging.getLogger(self.__class__.__name__)
        self._public = self._proxy_hander.public()
        self._volatile = set()

    def __getattr__(self, name):
        if name in self.__dict__["_public"]:
            entry = self.__dict__["_public"][name]
            if entry["type"] == "function":
                return ProxifyCallable(self, name)
            elif entry["type"] == "object":
                return ProxifyObject(self, name)
            else:
                raise Exception("Type is unknow")
        
        return object.__getattribute__(self, name)
    
    @property
    def handler(self)->ProxyHandler:
        return self._proxy_hander
    
    @property
    def public(self)->dict:
        return self._public
    
    def add_volatile(self, name:str)->None:
        self._volatile.add(name)

    def remove_volatile(self, name:str)->None:
        self._volatile.discard(name)

    def destroy(self):
        # all volatile object should be self destroying
        for name in self._volatile:
            try:
                self._proxy_hander.call(f"{name}._destroy")
            except KeyError:
                pass
    
    def close(self):
        pass

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()
        self.close()
    
