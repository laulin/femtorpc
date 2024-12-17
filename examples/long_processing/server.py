import concurrent.futures
from time import sleep
from uuid import uuid4

from femtorpc.tcp_daemon import TCPDaemon

if __name__ == "__main__":
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
    tasks = dict()
    daemon = TCPDaemon("127.0.0.1", 6666)

    def long_job(delay):
        print(f"Starting with delay {delay}")
        sleep(delay)
        print(f"Ending with delay {delay}")
        return (delay+1)**3

    def do_long_job(delay):
        task = executor.submit(long_job, delay)
        task_id = uuid4()
        tasks[task_id] = task
        return task_id
    
    def get_long_job(task_id):

        result = tasks[task_id].result(0)
        del tasks[task_id]
  
    daemon.register(do_long_job)
    daemon.register(get_long_job)

    try:
        while True:
            daemon.run_once(10, True)
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()
        executor.shutdown()