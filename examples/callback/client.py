from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        def reverse(x):
            return x[::-1]
            
        print(f"proxy.remote_map(reverse, ('abc', 'def')) -> {proxy.remote_map(reverse, ('abc', 'def'))}")         