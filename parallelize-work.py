import itertools
import multiprocessing
from multiprocessing.pool import ThreadPool
import subprocess
from api_keys import api_keys

from utils import get_list_of_pypi_packages

round_robin = itertools.cycle(api_keys)

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

def work(sample, api_key):
    print(f"{bcolors.OKCYAN}Collecting data for:{bcolors.ENDC}", sample, f"{bcolors.FAIL} api key using:{bcolors.ENDC}", api_key)
    my_tool_subprocess = subprocess.Popen('python3 parallelized-worker.py {} {}'.format(sample, api_key), shell=True, stdout=subprocess.PIPE)
    my_tool_subprocess.wait()
    my_tool_subprocess.kill()

# we are using half CPU threads
# cpu_count = int(multiprocessing.cpu_count() / 2)
cpu_count = min(int(multiprocessing.cpu_count()), len(api_keys))
tp = ThreadPool(cpu_count)
for sample in get_list_of_pypi_packages():
    tp.apply_async(work, (sample, round_robin.__next__(),))

tp.close()
tp.join()