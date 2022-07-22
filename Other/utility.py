import time
import multiprocessing as mp
import numpy as np
from functools import partial
from typing import Callable, Any
from tqdm import tqdm
from typing import Union
from subprocess import Popen, PIPE


class JobMachine:
    """
    Reliably track the completion of tasks in a multiprocessing pool
    with a shared counter object that is shown in the terminal using a progress
    bar. Does not store the results of the tasks - assumes that the worker
    function does not return anything useful.
    """
    class JobCounter:
        """
        The shared counter
        """
        def __init__(self):
            self.counter = mp.RawValue('i', 0)
            self.lock = mp.Lock()

        def increment(self):
            """
            Increase the counter by 1
            :return:
            """
            with self.lock:
                self.counter.value += 1

        @property
        def value(self) -> int:
            """
            The number of jobs that have been completed
            :return:
            """
            return self.counter.value

    def __init__(
        self,
        processes: int,
        worker_func: Callable,
        args_list: list
    ) -> None:
        self.cpus = processes
        self.job_counter = self.JobCounter()
        self.worker_func = worker_func
        self.args_list = args_list
        self.total_jobs = len(self.args_list)
        self.pool = mp.Pool(
            processes=self.cpus,
            initializer=self.init_pool
        )

    def init_pool(self):
        """
        Used to initialize each separate process
        :return:
        """
        global JOB_COUNTER
        JOB_COUNTER = self.job_counter

    def start(self):
        """
        Start the multiprocessing
        :return:
        """
        self.pool.map_async(
            partial(self.worker, self.worker_func),
            self.args_list
        )
        with tqdm(total=self.total_jobs) as bar:
            while bar.n < self.total_jobs:
                bar.n = self.job_counter.value
                bar.refresh()
        self.pool.close()
        self.pool.join()
        assert self.value == self.total_jobs

    @staticmethod
    def worker(task: Callable, value: Any):
        """
        Call the provided worker_func and increment the counter when it is done
        :param task:
        :param value:
        :return:
        """
        task(value)
        JOB_COUNTER.increment()

    @property
    def value(self) -> int:
        """
        The number of jobs that have been completed
        :return:
        """
        return self.job_counter.value


def simple_run(
    command: Union[list[str], str]
) -> str:
    """
    A Python wrapper to execute commands in the terminal and store std::out
    :param command:
        The command to execute
    :return:
        Any output to the console
    """
    process = Popen(command, shell=True, stdout=PIPE)
    output = list()
    while True:
        output.append(process.stdout.readline().strip())
        if process.poll() is not None:
            break
    return '\n'.join([x.decode() for x in output])


def my_worker(value):
    """
    Test worker for demonstration purposes
    :param value:
        The amount of time to sleep
    :return:
    """
    time.sleep(value)


def main() -> None:
    machine = JobMachine(
        processes=5,
        worker_func=my_worker,
        args_list=np.random.random(100)
    )
    machine.start()


if __name__ == '__main__':
    main()
