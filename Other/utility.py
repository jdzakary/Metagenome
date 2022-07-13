import time
import multiprocessing as mp
from functools import partial
from typing import Callable, Any
from tqdm import tqdm


class JobMachine:

    class JobCounter:
        def __init__(self):
            self.counter = mp.RawValue('i', 0)
            self.lock = mp.Lock()

        def increment(self):
            self.lock.acquire()
            self.counter.value += 1
            self.lock.release()

        @property
        def value(self) -> int:
            return self.counter.value

    def __init__(
        self,
        processes: int,
        total_jobs: int,
        worker_func: Callable,
        args_list: list
    ) -> None:
        self.cpus = processes
        self.job_counter = self.JobCounter()
        self.total_jobs = total_jobs
        self.worker_func = worker_func
        self.args_list = args_list
        assert len(self.args_list) == self.total_jobs
        self.pool = mp.Pool(
            processes=self.cpus,
            initializer=self.init_pool
        )

    def init_pool(self):
        global JOB_COUNTER
        JOB_COUNTER = self.job_counter

    def start(self):
        self.pool.map_async(
            partial(self.worker, self.worker_func),
            self.args_list
        )
        with tqdm(total=self.total_jobs) as bar:
            old_value = self.job_counter.value
            while old_value < self.total_jobs:
                if self.job_counter.value != old_value:
                    old_value = self.job_counter.value
                    bar.update(1)
        self.pool.close()
        self.pool.join()
        assert self.value == self.total_jobs

    @staticmethod
    def worker(task: Callable, value: Any):
        task(value)
        JOB_COUNTER.increment()

    @property
    def value(self) -> int:
        return self.job_counter.value


def hello(value):
    time.sleep(value)


def main() -> None:
    machine = JobMachine(
        processes=5,
        total_jobs=50,
        worker_func=hello,
        args_list=[1 for _ in range(50)]
    )
    machine.start()


if __name__ == '__main__':
    main()
