import os
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor
import glob
import argparse

N_WORKERS = 4


class Batcher:
    def __init__(self, folder, what, arguments):
        self.folder = folder
        self.what = what
        self.arguments = arguments
        self.futures = set()
        self.file_names = [f for f in glob.glob(f"{self.folder}/*.txt")]

    def push(self, future):
        self.futures.add(future)

    def pop(self, future):
        self.futures.remove(future)

    def wait(self):
        while len(self.futures) >= N_WORKERS:
            time.sleep(0.1)

    def next(self):
        return self.file_names.pop(0)

    def runnable(self, what, arguments):
        def _runnable(file_name):
            p = subprocess.Popen(
                f'.\\venv\\Scripts\\activate && py {what} -f "{file_name}" {arguments}', shell=True)
            p.wait()

        return _runnable

    def run(self):
        executor = ThreadPoolExecutor(max_workers=N_WORKERS)

        while True:
            self.wait()

            if len(self.file_names) == 0:
                break

            future = executor.submit(self.runnable(
                self.what, self.arguments), self.next())
            future.add_done_callback(self.pop)

            self.push(future)

        executor.shutdown(wait=True, cancel_futures=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Batching',
    )
    parser.add_argument(
        '-F', '--folder',
        type=str, help='Folder path to the time series file(s)',
        default=""
    )
    parser.add_argument(
        '-w', '--what',
        type=str, help='What to batch',
        default=""
    )
    parser.add_argument(
        '-a', '--arguments',
        type=str, help='Arguments to forward to python file',
        default=""
    )

    args = parser.parse_args()

    if len(args.folder) == 0:
        raise Exception('Pass a folder!')

    if len(args.what) == 0 or not args.what.endswith(".py"):
        raise Exception('Pass a python file!')

    Batcher(args.folder, args.what, args.arguments).run()
