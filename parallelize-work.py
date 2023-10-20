import multiprocessing
from multiprocessing.pool import ThreadPool
import subprocess

from utils import get_list_of_pypi_packages


def work(sample):
    my_tool_subprocess = subprocess.Popen('python3 parallelized-worker.py {}'.format(sample), shell=True, stdout=subprocess.PIPE)
    line = False
    while line:
        myline = my_tool_subprocess.stdout.readline()

# we are using half CPU threads
tp = ThreadPool(int(multiprocessing.cpu_count() / 2))
for sample in get_list_of_pypi_packages():
    tp.apply_async(work, (sample,))

tp.close()
tp.join()