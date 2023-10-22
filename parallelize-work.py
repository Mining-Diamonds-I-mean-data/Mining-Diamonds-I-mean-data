import itertools
import multiprocessing
from multiprocessing.pool import ThreadPool
import subprocess
from api_keys import api_keys
from threading import BoundedSemaphore, Timer, Lock
import time
from utils import get_list_of_pypi_packages


class RatedSemaphore(BoundedSemaphore):
    """Limit to 1 request per `period / value` seconds (over long run)."""

    def __init__(self, value=1, period=1):
        BoundedSemaphore.__init__(self, value)
        t = Timer(period, self._add_token_loop,
                  kwargs=dict(time_delta=float(period) / value))
        t.daemon = True
        t.start()

    def _add_token_loop(self, time_delta):
        """Add token every time_delta seconds."""
        while True:
            try:
                BoundedSemaphore.release(self)
            except ValueError:  # ignore if already max possible value
                pass
            time.sleep(time_delta)  # ignore EINTR

    def release(self):
        pass  # do nothing (only time-based release() is allowed)


class ApiKeyCycle:
    def __init__(self, api_keys=None):
        if api_keys is None:
            api_keys = []
        self.api_keys = api_keys
        self.semiphores = []
        self.index = 0
        self.end = len(api_keys)
        for i in range(len(api_keys)):
            self.semiphores.append(RatedSemaphore(value=59, period=60))

    def __next__(self):
        with self.semiphores[self.index]:
            item = self.api_keys[self.index]
        if self.index + 1 == self.end:
            self.index = 0
        else:
            self.index += 1
        return item


round_robin = ApiKeyCycle(api_keys)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def init_worker(rbg):
    global round_robin_global
    round_robin_global = rbg

mutex = Lock()

def work(sample, index, list_of_package_total):
    global round_robin_global, mutex
    # we are using a mutex on this and in next a round robin which limits an api key to be used 59 times a minute
    # if the semiphore holds the mutex other threads will be blocked, but that is ok as at least we won't exceed the api
    # rate limit
    with mutex:
        api_key = round_robin_global.__next__()
    print(f"{bcolors.OKCYAN}Collecting data for:{bcolors.ENDC}", sample, f"{bcolors.FAIL} api key using:{bcolors.ENDC}",
          api_key, f"{bcolors.OKGREEN}Progress:{bcolors.ENDC}",
          '{:.2%} ({}/{})'.format(index / list_of_package_total, index, list_of_package_total))
    try:
        my_tool_subprocess = subprocess.check_call(['python3', 'parallelized-worker.py', sample, api_key])
        print(f"{bcolors.OKBLUE}Done Collecting data for:{bcolors.ENDC}", sample,
              f"{bcolors.OKGREEN} Success{bcolors.ENDC}", my_tool_subprocess)
    except subprocess.CalledProcessError as e:
        print(f"{bcolors.OKBLUE}Done Collecting data for:{bcolors.ENDC}", sample,
              f"{bcolors.WARNING} Failed{bcolors.ENDC}", e)


# we are using half CPU threads
# cpu_count = int(multiprocessing.cpu_count() / 2)
cpu_count = min(int(multiprocessing.cpu_count()), len(api_keys))
tp = ThreadPool(cpu_count, initializer=init_worker, initargs=(round_robin,))
list_of_packages = get_list_of_pypi_packages()
list_of_package_total = len(list_of_packages)
for index, sample in enumerate(list_of_packages):
    tp.apply_async(work, (sample, index, list_of_package_total))

tp.close()
tp.join()
