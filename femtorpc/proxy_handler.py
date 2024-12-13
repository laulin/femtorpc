import logging

import dill

from femtorpc.request import Call, Public
from femtorpc.response import Response

class ProxyHandler:
    def __init__(self, callback, loads=dill.loads, dumps=dill.dumps):
        self._loads = loads
        self._dumps = dumps
        self._callback = callback
        self._log = logging.getLogger(self.__class__.__name__)


    def call(self, name:str, *args, **kwargs):
        call = Call(name, args, kwargs)
        self._log.debug("call ", call)
        call_stream = self._dumps(call)

        response_stream = self._callback(call_stream)

        response:Response = self._loads(response_stream)
        self._log.debug("response " , response)
        if response.exception is not None:
            raise response.exception
        
        return response.return_value
    
    def public(self)->dict:
        call = Public()
        call_stream = self._dumps(call)

        response_stream = self._callback(call_stream)

        response:Response = self._loads(response_stream)

        if response.exception is not None:
            raise response.exception
        
        return response.return_value


    