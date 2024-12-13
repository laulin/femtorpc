import unittest

from femtorpc.proxy_wrapper import ProxyWrapper
from femtorpc.command_handler import CommandHandler
from femtorpc.response import Function

class TestProxyWrapper(unittest.TestCase):
    def test_call(self):
        def foo(x)->int:
            return x + 1
        
        command_hander = CommandHandler()
        command_hander.register("foo", foo)

        proxy_wrapper = ProxyWrapper(command_hander.call)

        results = proxy_wrapper.foo(10)
        self.assertEqual(results, 11)

    def test_remote_call(self):
        def foo(x):
            def bar(y)->int:
                return x +y
            return bar
        
        command_hander = CommandHandler()
        command_hander.register("foo", foo)

        proxy_wrapper = ProxyWrapper(command_hander.call)

        bar = proxy_wrapper.foo(10)
        self.assertEqual(bar(1), 11)

    def test_remote_generator(self):
        def foo():
            for i in range(3):
                yield i
        
        command_hander = CommandHandler()
        command_hander.register("foo", foo)

        proxy_wrapper = ProxyWrapper(command_hander.call)

        bar = proxy_wrapper.foo()
        results = [i for i in bar]
        self.assertListEqual(results, [0,1,2])

    def test_remote_generator_partial(self):
        def foo():
            for i in range(3):
                yield i
        
        command_hander = CommandHandler()
        command_hander.register("foo", foo)

        proxy_wrapper = ProxyWrapper(command_hander.call)

        bar = proxy_wrapper.foo()
        results = [next(bar) for i in range(2)] # pending
        self.assertListEqual(results, [0,1])

    def test_object(self):
        class foo:
            def bar(self):
                return 3
        
        local_foo = foo()
        command_hander = CommandHandler()
        command_hander.register("foo", local_foo)

        proxy_wrapper = ProxyWrapper(command_hander.call)

        myfoo = proxy_wrapper.foo
        results = myfoo.bar()
        self.assertEqual(results, 3)


