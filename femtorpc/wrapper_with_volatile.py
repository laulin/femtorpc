import inspect
from typing import Tuple, Union
import re
from uuid import uuid4

from femtorpc.wrapper import Wrapper
from femtorpc.response import Function, Generator


class WrapperWithVolatile(Wrapper):
    # some returned value must stay in server side to prevent loosing context
    # or because they can't be serialized. Such object are called here volatiles.
    def __init__(self, max_volatile:int=1000):
        super().__init__()
        self._volatiles = dict()
        self._max_volatile = max_volatile

    def _register_volatile(self, result:object, as_object:Union[Generator, Function])->Union[Generator, Function]:
        result_id = "*" + str(uuid4())
        if len(self._volatiles) >= self._max_volatile:
            raise OverflowError(f"Max volatile reaches")
        
        self._volatiles[result_id] = result
        return as_object(result_id)
    
    def _call_volatile(self, name, *args, **kwargs)->Tuple[Union[object, None], Union[Exception, None]]:
        elements = name.split(".")
        object_id = elements[0]
        function_name = elements[1] if len(elements) > 1 else None

        if function_name == "_destroy":
            if object_id not in self._volatiles:
                return None, KeyError(function_name)
            
            del self._volatiles[object_id]
            return None, None
        
        try:
            obj = self._volatiles[object_id]
            if function_name is not None:
                function = getattr(obj, function_name)
            else:
                function = obj
        except:
            return None, AttributeError(f"{object_id}.{function_name} doesn't exist")
        
        try:
            return_value, exception = self.generic_call(function, None, *args, **kwargs)

            if inspect.isgenerator(return_value):
                return_value = self._register_volatile(return_value, Generator)

            if inspect.isfunction(return_value):
                return_value = self._register_volatile(return_value, Function)


            if isinstance(exception, StopIteration):
                del self._volatiles[object_id]
            return return_value, exception
        except Exception as e:
            return None, e
        
    
    def call(self, name:str, *args, **kwargs)->Tuple[Union[object, None], Union[Exception, None]]:
        if re.match(r"^[a-zA-F]", name):
            # common case, exposed function
            result, exception = super().call(name, *args, **kwargs)
        elif re.match(r"^\*[0-9a-f\-]+", name):
            # volatile case
            result, exception = self._call_volatile(name, *args, **kwargs)
        else:
            return None, Exception("Function name is inconsistent")
            
        if exception is not None:
            return result, exception
        
        try:
            if inspect.isgenerator(result):
                result = self._register_volatile(result, Generator)

            if inspect.isfunction(result):
                result = self._register_volatile(result, Function)
        except Exception as e:
            return None, e

        return result, exception


    