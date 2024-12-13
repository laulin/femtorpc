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