from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        print(f"proxy.add(1,2) -> {proxy.add(1,2)}")
        try:
            print(f"proxy.add(1,2) -> {proxy.add(1.0,2)}")
        except Exception as e:
            print(f"Ooops {type(e)} : {e}")
