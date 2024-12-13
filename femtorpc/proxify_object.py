import logging

from femtorpc.proxify_callable import ProxifyCallable

class ProxifyObject:
    def __init__(self, proxy, name:str):
        self._proxy = proxy
        self._name = name
        logging.getLogger(f"{self.__class__.__name__}({name})@{self}")

    def __getattr__(self, name):
        full_name = f"{self._name}.{name}"
        if full_name in self._proxy.public:
            entry = self._proxy.public[full_name]
            if entry["type"] == "function":
                return ProxifyCallable(self._proxy, full_name)
            else:
                raise Exception("Type is unknow")
        
        return object.__getattribute__(self, full_name)