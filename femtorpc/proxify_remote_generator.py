import logging

class ProxifyRemoteGenerator:
    def __init__(self, proxy, name:str):
        self._proxy = proxy
        self._name = name
        logging.getLogger(f"{self.__class__.__name__}({name})@{self}")
        self._proxy.add_volatile(name)

    def destroy(self):
            self._proxy.handler.call(f"{self._name}._destroy")
            self._proxy.remove_volatile(self._name)

    def __iter__(self):
        return self

    def __next__(self):
        # is StopIteration is raised, volatile object is automatically deleted in server side
        return self._proxy.handler.call(f"{self._name}.__next__")

    def send(self, value):
        return self._proxy.handler.call(f"{self._name}.send", value)

    def throw(self, exception):
        try:
            self._proxy.handler.call(f"{self._name}.throw", exception)
        except Exception as e:
            raise e
        finally:
            self.destroy()

    def close(self):
        try:
            self._proxy.handler.call(f"{self._name}.close")
        except Exception as e:
            raise e
        finally:
            self.destroy()