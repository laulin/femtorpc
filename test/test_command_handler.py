import unittest

from femtorpc.command_handler import CommandHandler
from femtorpc.proxy_handler import ProxyHandler
from femtorpc.response import Function

class TestCommandHandler(unittest.TestCase):
    def test_call(self):
        command_hander = CommandHandler()
        proxy_handler = ProxyHandler(command_hander.call)

        def foo(x)->int:
            return x + 1

        command_hander.register(foo, "foo")
        result = proxy_handler.call("foo", 10)
        self.assertEqual(result, 11)

    def test_closure(self):
        command_hander = CommandHandler()
        proxy_handler = ProxyHandler(command_hander.call)

        def foo(x:int):
            def bar(y:int)->int:
                return x + y
            return bar

        command_hander.register(foo, "foo")
        result = proxy_handler.call("foo", 10)
        self.assertTrue(isinstance(result, Function))

    def test_exception(self):
        command_hander = CommandHandler()
        proxy_handler = ProxyHandler(command_hander.call)

        def foo():
            raise Exception("Nope")

        command_hander.register(foo, "foo")
        with self.assertRaises(Exception) as context:
            proxy_handler.call("foo")
        
