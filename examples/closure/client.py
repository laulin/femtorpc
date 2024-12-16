from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        add = proxy.build_add(4)
        print(f"inc(10) -> {add(10)}")