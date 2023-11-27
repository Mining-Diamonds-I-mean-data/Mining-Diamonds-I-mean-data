import multiprocessing
from multiprocessing.pool import ThreadPool
import subprocess
from utils import get_list_of_new_pypi_and_database_packages, dump_database_csv


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


# How many python processes do you want to run at a time to collect data
python_process_count_to_spawn = int(multiprocessing.cpu_count())
tp = ThreadPool(python_process_count_to_spawn)
list_of_packages = get_list_of_new_pypi_and_database_packages()
list_of_package_total = len(list_of_packages)


def work(sample, index, list_of_package_total):
    print(f"{bcolors.OKCYAN}Collecting data for:{bcolors.ENDC}", sample, f"{bcolors.OKGREEN}Progress:{bcolors.ENDC}",
          '{:.2%} ({}/{})'.format(index / list_of_package_total, index, list_of_package_total))
    try:
        my_tool_subprocess = subprocess.check_call(['python3', 'parallelized-worker.py', sample])
        print(f"{bcolors.OKBLUE}Done Collecting data for:{bcolors.ENDC}", sample,
              f"{bcolors.OKGREEN} Success{bcolors.ENDC}", my_tool_subprocess)
    except subprocess.CalledProcessError as e:
        if e.returncode == 144:
            print(f"{bcolors.FAIL}Failed requesting release Re-adding to queue:{bcolors.ENDC}", sample)
            tp.apply_async(work, (sample, index, list_of_package_total))
        elif e.returncode == 66:
            print(f"{bcolors.FAIL}Library doesn't exist on pypi removing from queue:{bcolors.ENDC}", sample)
        else:
            print(f"{bcolors.FAIL}Done Collecting data for:{bcolors.ENDC}", sample,
                  f"{bcolors.WARNING} Failed unknown reason {bcolors.ENDC}", e)


for index, sample in enumerate(list_of_packages):
    tp.apply_async(work, (sample, index, list_of_package_total))

tp.close()
tp.join()

# dump the database as a csv file whenever this is run
dump_database_csv()
