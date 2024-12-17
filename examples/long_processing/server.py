import concurrent.futures
from time import sleep
from uuid import uuid4

from femtorpc.tcp_daemon import TCPDaemon

class AsyncCall:
    def __init__(self, function, max_workers:int):
        self._executor = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
        self._tasks = dict()
        self._function = function

    def do(self, *args, **kwargs):
        task = self._executor.submit(self._function, *args, **kwargs)
        task_id = uuid4()
        self._tasks[task_id] = task
        def _get_result():
            result = self._tasks[task_id].result(0)
            del self._tasks[task_id]
            return result
        return _get_result

    def close(self):
        self._executor.shutdown()

if __name__ == "__main__":
    def long_job(delay):
        print(f"Starting with delay {delay}")
        sleep(delay)
        print(f"Ending with delay {delay}")
        return (delay+1)**3

    async_call = AsyncCall(long_job, 2)
    daemon = TCPDaemon("127.0.0.1", 6666)

    daemon.register(async_call.do, "long_job")

    try:
        while True:
            daemon.run_once(10, True)
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()
        async_call.close()