import unittest

from femtorpc.wrapper import Wrapper

class TestWrapper(unittest.TestCase):
    def test_register_function(self):
        def foo(a:int, b:str, c)->list:
            return [a,b,c]
        
        wrapper = Wrapper()
        wrapper.register("foo", foo)

    def test_register_object(self):
        class Bar:
            def __init__(self, xxx:str):
                self._xxx = xxx
            
            def f(self)->str:
                return self._xxx
            
        bar = Bar("test")
        
        wrapper = Wrapper()
        wrapper.register("bar", bar)

    def test_call_function(self):
        def foo(a:int, b:str, c)->list:
            return [a,b,c]
        
        wrapper = Wrapper()
        wrapper.register("foo", foo)

        results = wrapper.call("foo", 1, "2", 3)
        expected = ([1, "2", 3], None)

        self.assertEqual(results, expected)

    def test_call_function_bad_arg_number(self):
        # check number and position argument and must failed if an argument miss
        def foo(a:int, b:str, c)->list:
            return [a,b,c]
        
        wrapper = Wrapper()
        wrapper.register("foo", foo)

        results = wrapper.call("foo", 1, "2")
        

        self.assertTrue(isinstance(results[1], TypeError))

    def test_call_function_bad_arg_type(self):
        # check argument typing and must failed if typing is bad
        def foo(a:int, b:str, c)->list:
            return [a,b,c]
        
        wrapper = Wrapper()
        wrapper.register("foo", foo)

        results = wrapper.call("foo", 1, 2, 3)
        

        self.assertTrue(isinstance(results[1], TypeError))