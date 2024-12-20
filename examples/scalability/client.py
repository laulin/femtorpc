from collections import Counter
from pprint import pprint

from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    # This part call 100 times the foo() function, ignoring there are multiple processes.
    # Counter is used to show how spread calls are done on multiple processes.
    with TCPProxy("127.0.0.1", 6666) as proxy:
        count_process = Counter()
        for i in range(100):
            count_process[proxy.foo()] += 1

        pprint(count_process)

    