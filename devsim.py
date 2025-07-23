"""
This is just a playbed for some synthetic benchmark ideas.
The goals are:
1. deterministic.
2. scorable
3. indicative of real world performance

on a side note, i now realize why writing something like a geekbench clone is really hard
maybe I should just USE geekbench (or a clone).
"""

import os
import subprocess
import time
import math
import tempfile
import random


def events_per_second(name="task"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            count = func(*args, **kwargs)
            end = time.time()
            duration = end - start
            eps = count / duration if duration > 0 else 0
            print(f"{name}: {count} events in {duration:.2f}s ({eps:.2f} events/sec)")
            return count

        return wrapper

    return decorator


def quick_bench(time_secs: int) -> list[str]:
    """
    Sysbench is deterministic and gives some kind of score
    """
    command = ["sysbench", "--threads=8", f"--time={time_secs}", "cpu", "run"]
    output = subprocess.check_output(command)

    lines = output.decode("utf-8").split("\n")
    for line in lines:
        if "events per second:" in line:
            return [line]
    return lines


def is_prime(n: int) -> bool:
    """
    quick and dirty prime check. this doesn't need to be bullet proof
    I also don't care about negative numbers
    """
    if n <= 3:
        return True
    sqrt = int(math.sqrt(n))
    for i in range(2, sqrt + 1):
        if n % i == 0:
            return False
    return True


@events_per_second("CPU")
def cpu_task(num_primes: int = 500) -> int:
    count = 0
    for i in range(2, num_primes):
        if is_prime(i):
            count += 1
    return count


def dev_workload(duration_secs):
    """
    Simulate a developer workload for the given duration
    """
    start = time.time()
    tmpdir = tempfile.mkdtemp()

    while (time.time() - start) < duration_secs:
        print(f"elapsed time {(time.time() - start)}")
        cpu_burst()
        io_burst(tmpdir)
        memory_use()
        time.sleep(random.uniform(1.0, 2.0))  # idle pause

    try:
        for f in os.listdir(tmpdir):
            os.remove(os.path.join(tmpdir, f))
        os.rmdir(tmpdir)
    except Exception:
        pass  # Not critical if cleanup fails
