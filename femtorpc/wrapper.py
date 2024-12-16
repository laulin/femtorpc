import inspect
import logging
from typing import Tuple, Union
from collections import namedtuple

# EmptySignature and CreateSignature are used to mock inspect.Signature behaviour.
# Used in case of empty signature on built-in function
EmptySignature = namedtuple("EmptySignature", ["args", "kwargs"])

class CreateSignature:
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def bind(self, function)->EmptySignature:
        return EmptySignature(self.args, self.kwargs)

class Wrapper:
    def __init__(self):
        self._register = dict()
        self._log = logging.getLogger(self.__class__.__name__)


    def enforce_annotations(self, func):
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            for name, value in bound_args.arguments.items():
                if name in func.__annotations__:
                    expected_type = func.__annotations__[name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"'{name}' parameters is expected as as {expected_type} not {type(value)}"
                        )

            result = func(*args, **kwargs)

            if 'return' in func.__annotations__:
                expected_return_type = func.__annotations__['return']
                if expected_return_type is not None: 
                    if not isinstance(result, expected_return_type):
                        raise TypeError(
                            f"Return type is expected as {expected_return_type}, not {type(result)}"
                        )

            return result
        
        return wrapper
    
    def register(self, obj:object, name:str=None):
        if name is None:
            try:
                name = obj.__name__
            except AttributeError:
                raise Exception("Object must have an attribute __name__ or an explicite via the name parameter")
            
        if name.startswith("_"):
            raise Exception("Protected or private function can't be registered")
        
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            self._register[name] = {
                "callable" : self.enforce_annotations(obj),
                "signature" : inspect.signature(obj),
                "type": "function"
            }
        elif not inspect.isclass(obj) and isinstance(obj, object):
            self._register[name] = {
                "callable" : None,
                "signature" : None,
                "type": "object"
            }
            for member_name, member_callable in inspect.getmembers(obj):
                if not member_name.startswith("_"):  
                    self.register(member_callable, name+"."+member_name)
        else:
            raise Exception("object type is not supported")


    def call(self, name, *args, **kwargs)->Tuple[Union[object, None], Union[Exception, None]]:
        if name not in self._register:
            return (None, ValueError(f"{name} is not callable"))
        func = self._register[name]["callable"]
        signature = self._register[name]["signature"]
        return self.generic_call(func, signature, *args, **kwargs)
        
    def generic_call(self, func:callable, signature, *args, **kwargs)->Tuple[Union[object, None], Union[Exception, None]]:
        if signature is None:
            try:
                signature = inspect.signature(func)
            except ValueError:
                # is no signature exist, we ignore it
                signature = CreateSignature(args, kwargs)
        try:
                params = signature.bind(*args, **kwargs)
                return (func(*params.args, **params.kwargs), None)
        except Exception as e:
            return (None, e)
        
    def get_registered(self)->dict:
        output = dict()
        for name, value in self._register.items():
            output[name] = {"type" : value["type"], "signature" : value["signature"]}

        return output

    