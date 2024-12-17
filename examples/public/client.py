from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        exposed_function = proxy.public

    # ...

    with TCPProxy("127.0.0.1", 6666, 100, public=exposed_function) as proxy_b:
        print(f"proxy_b.foo(10) -> {proxy_b.foo(10)}")