from femtorpc.tcp_proxy import TCPProxy
from femtorpc.serializer import get_serializer

KEY = b"00000000000000000000000000000000"
COMPRESSED = True

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100, **get_serializer(KEY, COMPRESSED)) as proxy:
        print(f"proxy.add(1,2) -> {proxy.add(1,2)}")
