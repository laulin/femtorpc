from femtorpc.tcp_daemon import TCPDaemon

if __name__ == "__main__":
    daemon = TCPDaemon("127.0.0.1", 6666)
    def build_add(to_add):
        def add(value):
            return value + to_add
        return add
    
    daemon.register(build_add)

    try:
        while True:
            daemon.run_once(10, True)
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()