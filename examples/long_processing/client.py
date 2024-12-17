import time
import concurrent.futures

from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        async_result_1 = proxy.long_job(1)
        async_result_2 = proxy.long_job(2)
        
        time.sleep(0.5)

        try:
            async_result_1()
        except concurrent.futures._base.TimeoutError:
            print("job not finished")

        time.sleep(0.6)
        print(f"Results 1 : {async_result_1()}")
        time.sleep(1)
        print(f"Results 2 : {async_result_2()}")

