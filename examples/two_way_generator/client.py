from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        x = proxy.square()
        next(x) # initializing the generator
        for i in (1,2,3,0):
            print(x.send(i))