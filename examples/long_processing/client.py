import time
import concurrent.futures

from femtorpc.tcp_proxy import TCPProxy

if __name__ == "__main__":
    with TCPProxy("127.0.0.1", 6666, 100) as proxy:
        task_id_1 = proxy.do_long_job(1)
        task_id_2 = proxy.do_long_job(3)
        
        time.sleep(0.5)

        try:
            proxy.get_long_job(task_id_1)
        except concurrent.futures._base.TimeoutError:
            print("job not finished")

        time.sleep(0.6)
        print(f"Results : {proxy.get_long_job(task_id_1)}")

