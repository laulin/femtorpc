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