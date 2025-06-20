import os
import subprocess
import time
import hashlib
import tempfile
import random


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


def cpu_burst(work_size: int = 1_000_000):
    """
    Simulate CPU-bound load similar to sorting or compiling
    """
    data = [random.random() for _ in range(work_size)]
    data.sort()


def io_burst(tmpdir: str = "/tmp", file_size: int = 10**6, file_count: int = 5):
    """
    Simulate disk I/O: write and read several files
    """
    for i in range(file_count):
        path = os.path.join(tmpdir, f"tempfile_{i}.txt")
        with open(path, "w") as f:
            f.write("A" * file_size)
        with open(path, "rb") as f:
            hashlib.sha256(f.read()).hexdigest()


def memory_use(size: int = 10_000_000):
    """
    Allocate and process a large list to simulate memory usage
    """
    data = list(range(size))
    total = sum(data)
    del data
    return total


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
