# femtorpc

FemtoRPC is a minimalist Remote Procedure Call (RPC) library built on ZeroMQ for network communication. It is designed to be simple, robust, and lightweight, enabling efficient interactions between remote processes, with security in mind.

# Installation

To install FemtoRPC, you can use pip to clone and install it directly from the GitHub repository:

``` bash
pip install git+https://github.com/laulin/femtorpc.git
```

# Usages
All examples are availables in examples/ but let see them in details.

## Basic
The most basic usage can be sum up with this example :

client :
``` python
from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        print(f"proxy.foo(1) -> {proxy.foo(1)}") 
        print(f"proxy.my_object.bar('hello') -> {proxy.my_object.reverse('hello')}") 
```

server :
``` python
from femtorpc.tcp_daemon import TCPDaemon

if __name__ == "__main__":
    daemon = TCPDaemon("127.0.0.1", 6666)
    def foo(x)->int:
        return x + 1
    
    class Stuff:
        def reverse(self, data:str)->str:
            return data[::-1]
    
    daemon.register(foo)
    stuff = Stuff()
    daemon.register(stuff, "my_object")

    try:
        while True:
            daemon.run_once(10, True)
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()
```

On the server side, we register a function (foo) and an instance of Stuff (stuff). The registration of foo is done using function name (implicit naming), meanwhile class instance need an explicite name (here my_object). This is due to the fact Stuff doesn't have ``__name__`` attribute. Explicite naming always override implicite name. 

No method or function whose name starts "_" (protected or private) can be registered. This way, if Stuff owns a method ``_do_something``, it wouldn't be exposed to client. 

## Generator as return value

Generator is a powerful python toy, efficient for lazyness. And we love be lazy ! In FemtoRPC, generator object stay in the server side and are proxified to the client. Generators are destoyed when an exception is raised or if the proxy is closed.

https://realpython.com/introduction-to-python-generators/

client :

``` python
from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        for i in proxy.square(3):
            print(i)
```
server :
``` python
from femtorpc.tcp_daemon import TCPDaemon

if __name__ == "__main__":
    daemon = TCPDaemon("127.0.0.1", 6666)
    def square(x):
        for i in range(3):
            yield x**i
    
    
    daemon.register(square)

    try:
        while True:
            daemon.run_once(10, True)
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()
```

Generators also work in two way behaviour :

client :

``` python
from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        x = proxy.square()
        next(x) # initializing the generator
        for i in (1,2,3,0):
            print(x.send(i))
```
server :
``` python
from femtorpc.tcp_daemon import TCPDaemon

if __name__ == "__main__":
    daemon = TCPDaemon("127.0.0.1", 6666)
    def square():
        x = 1
        while True:
            x = yield x**2
    
    daemon.register(square)

    try:
        while True:
            daemon.run_once(10, True)
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()
```