from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        print(f"proxy.foo(1) -> {proxy.foo(1)}") 
        print(f"proxy.my_object.bar('hello') -> {proxy.my_object.reverse('hello')}") 