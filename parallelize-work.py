import itertools
import multiprocessing
from multiprocessing.pool import ThreadPool
import subprocess
from api_keys import api_keys

from utils import get_list_of_pypi_packages, progressBar

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
    try:
        my_tool_subprocess = subprocess.check_call(['python3', 'parallelized-worker.py', 'sample', 'api_key'])
        print(f"{bcolors.OKBLUE}Done Collecting data for:{bcolors.ENDC}", sample, f"{bcolors.OKGREEN} Success{bcolors.ENDC}", my_tool_subprocess)
    except subprocess.CalledProcessError as e:
        print(f"{bcolors.OKBLUE}Done Collecting data for:{bcolors.ENDC}", sample,f"{bcolors.WARNING} Failed{bcolors.ENDC}", e)

# we are using half CPU threads
# cpu_count = int(multiprocessing.cpu_count() / 2)
cpu_count = min(int(multiprocessing.cpu_count()), len(api_keys))
tp = ThreadPool(cpu_count)
list_of_packages = get_list_of_pypi_packages()
list_of_package_total = len(list_of_packages)
for index, sample in enumerate(list_of_packages):
    tp.apply_async(work, (sample, round_robin.__next__(),))
    print(f"{bcolors.OKGREEN}Progress:{bcolors.ENDC}", str(index) + "/" + str(list_of_package_total))

tp.close()
tp.join()