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
```

server :
``` python
from femtorpc.tcp_daemon import TCPDaemon

if __name__ == "__main__":
    daemon = TCPDaemon("127.0.0.1", 6666)
    def foo(x)->int:
        return x + 1
    
    daemon.register("foo", foo)

    try:
        while True:
            daemon.run_once(10, True)
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()
```