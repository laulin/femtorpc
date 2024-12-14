import logging

import dill

from femtorpc.wrapper_with_volatile import WrapperWithVolatile
from femtorpc.request import Call, Public
from femtorpc.response import Response



class CommandHandler:
    def __init__(self, loads=dill.loads, dumps=dill.dumps):
        self._wrapper = WrapperWithVolatile()
        self._loads = loads
        self._dumps = dumps
        self._log = logging.getLogger(self.__class__.__name__)

    def register(self, obj:object, name:str=None):
        self._wrapper.register(obj, name)

    def call(self, data_stream:bytes)->bytes:
        command = self._loads(data_stream)
        return_value, exception = None, None
        if isinstance(command, Call):
            return_value, exception = self._wrapper.call(command.name, *command.args, **command.kwargs)
        elif isinstance(command, Public):
            return_value = self._wrapper.get_registered()
        else:
            exception = Exception("Unknow command")

        response = Response(return_value, exception)

        return self._dumps(response)
                            
