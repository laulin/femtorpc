import unittest

from femtorpc.wrapper_with_volatile import WrapperWithVolatile
from femtorpc.wrapper_with_volatile import Generator, Function

class TestWrapperWithVolatile(unittest.TestCase):
    def test_generator(self):
        def foo():
            for i in range(3):
                yield i
        wrapper = WrapperWithVolatile()
        wrapper.register(foo, "foo")

        results = wrapper.call("foo")

        self.assertTrue(isinstance(results[0], Generator))

    def test_closure(self):
        def foo(x):
            def bar()->int:
                return x+1
            return bar
        
        wrapper = WrapperWithVolatile()
        wrapper.register(foo, "foo")

        results = wrapper.call("foo", "1")

        self.assertTrue(isinstance(results[0], Function))

    def test_generator_call_1(self):
        def foo():
            for i in range(3):
                yield i
        wrapper = WrapperWithVolatile()
        wrapper.register(foo, "foo")

        generator, _ = wrapper.call("foo")
        
        results = wrapper.call(f"{generator.id}.__next__")
        self.assertEqual(results, (0, None))

    def test_generator_call_all(self):
        def foo():
            for i in range(3):
                yield i
        wrapper = WrapperWithVolatile()
        wrapper.register(foo, "foo")

        generator, _ = wrapper.call("foo")
        
        results = [wrapper.call(f"{generator.id}.__next__") for i in range(4)]
        self.assertTrue(isinstance(results[3][1], StopIteration))

    def test_generator_del(self):
        def foo():
            for i in range(3):
                yield i
        wrapper = WrapperWithVolatile()
        wrapper.register(foo, "foo")

        generator, _ = wrapper.call("foo")
        
        wrapper.call(f"{generator.id}._destroy")
        # must not work since generator doesn't exist anymore
        _, exception = wrapper.call(f"{generator.id}.__next__")
        self.assertTrue(isinstance(exception, AttributeError))

    def test_generator_call_send(self):
        def square():
            x = 1
            while True:
                x = yield x**2
        wrapper = WrapperWithVolatile()
        wrapper.register(square)

        # prepare the generator
        generator, _ = wrapper.call("square")
        wrapper.call(f"{generator.id}.__next__")
 
        results = wrapper.call(f"{generator.id}.send", 10)
        self.assertEqual(results, (100, None))
    
    def test_generator_auto_del(self):
        def foo():
            for i in range(3):
                yield i
        wrapper = WrapperWithVolatile()
        wrapper.register(foo, "foo")

        generator, _ = wrapper.call("foo")
        
        x = [wrapper.call(f"{generator.id}.__next__") for i in range(4)]
        # must not work since generator doesn't exist anymore
        _, exception = wrapper.call(f"{generator.id}.__next__")
        self.assertTrue(exception, AttributeError)


    def test_closure_del(self):
        def foo(x):
            def bar()->int:
                return x+1
            return bar
        
        wrapper = WrapperWithVolatile()
        wrapper.register(foo, "foo")

        closure, _ = wrapper.call("foo", "1")
        
        wrapper.call(f"{closure.id}._destroy")
        # must not work since generator doesn't exist anymore
        _, exception = wrapper.call(f"{closure.id}", 2)
        self.assertTrue(isinstance(exception, AttributeError))

    def test_closure_of_closure(self):
        def foo(x):
            def bar(y):
                def stuff():
                    return x+y
                return stuff
            return bar
        
        wrapper = WrapperWithVolatile()
        wrapper.register(foo, "foo")

        result, _ = wrapper.call("foo", 1)
        result2, _ = wrapper.call(f"{result.id}", 10) # bar
        result3, _ = wrapper.call(f"{result2.id}") # stuff

        self.assertEqual(result3, 11)