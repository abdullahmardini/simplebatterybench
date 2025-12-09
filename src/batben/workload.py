"""
This is just a playbed for some synthetic benchmark ideas.
The goals are (in order):
1. deterministic
2. scorable
3. indicative of real world performance

on a side note, i now realize why writing something like a geekbench clone is really hard
maybe I SHOULD just ise geekbench (or a clone).
"""

import math
import os
import random
import time

import httpx
import numpy as np


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


#  ██████╗██████╗ ██╗   ██╗
# ██╔════╝██╔══██╗██║   ██║
# ██║     ██████╔╝██║   ██║
# ██║     ██╔═══╝ ██║   ██║
# ╚██████╗██║     ╚██████╔╝
#  ╚═════╝╚═╝      ╚═════╝
def is_prime(n: int) -> bool:
    """
    quick and dirty prime check. this doesn't need to be bullet proof
    I also don't care about negative numbers
    """
    # This is basically to capture the base case
    if n <= 3:
        return True
    sqrt = int(math.sqrt(n))
    for i in range(2, sqrt + 1):
        if n % i == 0:
            return False
    return True


@events_per_second("CPU")
def cpu_task(num_primes: int = 500) -> int:
    print(f"Starting CPU task: finding number of primes up to {num_primes}")
    count = 0
    for i in range(2, num_primes):
        if is_prime(i):
            count += 1
        print(f"    {i} is prime bring the count to {count}.", end="\r")
    return count


# ███╗   ███╗███████╗███╗   ███╗
# ████╗ ████║██╔════╝████╗ ████║
# ██╔████╔██║█████╗  ██╔████╔██║
# ██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║
# ██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║
# ╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝
@events_per_second("MEM")
def mem_task(size_mb=100, iterations=50):
    """
    Allocates and fills a large list repeatedly.
    """
    # A standard Python int object is about 28 bytes in 64-bit
    chunk_size = int(size_mb * 1024 * 1024 / 28)

    print(f"Starting MEM task: {size_mb}MB chunks, {iterations} iterations.")
    for i in range(iterations):
        # 1. Allocation and Fill: Allocate a list and fill it with random data.
        # This stresses the memory allocation mechanism and the memory itself.
        big_list = [random.randint(0, 1000) for _ in range(chunk_size)]

        # 2. Minimal work on the list
        _ = sum(big_list) % 100  # Inefficiently calculate a hash/sum

        # 3. Deallocation: Delete the reference to free the memory.
        # This stresses the garbage collector and prepares for the next allocation.
        del big_list
        # Using gc.collect() can force the issue, but standard 'del' often suffices
        # and keeps the benchmark simpler.

        print(f"  Iteration {i + 1}/{iterations} complete.", end="\r")
        time.sleep(0.01)  # Add a slight pause to allow OS/GC to catch up
    return iterations


#  ██████╗ ██████╗ ██╗   ██╗
# ██╔════╝ ██╔══██╗██║   ██║
# ██║  ███╗██████╔╝██║   ██║
# ██║   ██║██╔═══╝ ██║   ██║
# ╚██████╔╝██║     ╚██████╔╝
#  ╚═════╝ ╚═╝      ╚═════╝
@events_per_second("GPU")
def gpu_task(matrix_size=512, iterations=10):
    """Repeatedly performs large matrix multiplications with NumPy."""
    print(f"Starting GPU/Math task: {matrix_size}x{matrix_size} matrices, {iterations} iterations.")
    for i in range(iterations):
        # Create large matrices, forces allocation and movement of data
        A = np.random.rand(matrix_size, matrix_size)
        B = np.random.rand(matrix_size, matrix_size)

        # Matrix multiplication (A @ B) is highly parallelizable and computationally intensive
        C = A @ B

        # Perform a simple operation on the result to ensure it's not optimized away
        _ = np.sum(C)

        print(f"  Iteration {i + 1}/{iterations} complete.", end="\r")
        # Explicitly delete to encourage deallocation
        del A, B, C
        time.sleep(0.01)
    return iterations


# ██╗ ██████╗
# ██║██╔═══██╗
# ██║██║   ██║
# ██║██║   ██║
# ██║╚██████╔╝
# ╚═╝ ╚═════╝
@events_per_second("IO")
def io_task(file_count=50, file_size_kb=4):
    """Creates, writes, reads, and deletes many files inefficiently."""
    test_dir = "temp_benchmark_io"
    os.makedirs(test_dir, exist_ok=True)
    file_size_bytes = file_size_kb * 1024

    print(f"Starting I/O task: {file_count} files, {file_size_kb}KB each.")
    for i in range(file_count):
        filename = os.path.join(test_dir, f"temp_file_{i}.txt")
        data_chunk = "A" * 100  # Small buffer for inefficient writes

        # 1. Write inefficiently
        with open(filename, "w") as f:
            for _ in range(file_size_bytes // 100):
                f.write(data_chunk)
            # Use os.fsync(f.fileno()) to force immediate disk write, adding stress
            os.fsync(f.fileno())

        # 2. Read inefficiently
        read_data = ""
        with open(filename, "r") as f:
            while True:
                chunk = f.read(1)  # Read one byte at a time
                if not chunk:
                    break
                read_data += chunk

        # 3. Delete
        os.remove(filename)

        print(f"  File {i + 1}/{file_count} processed.", end="\r")

    # Clean up the directory
    os.rmdir(test_dir)
    return file_count


# ███╗   ██╗███████╗████████╗
# ████╗  ██║██╔════╝╚══██╔══╝
# ██╔██╗ ██║█████╗     ██║
# ██║╚██╗██║██╔══╝     ██║
# ██║ ╚████║███████╗   ██║
# ╚═╝  ╚═══╝╚══════╝   ╚═╝
@events_per_second("NET")
def net_task(target_url="https://www.google.com/robots.txt", iterations=50):
    """Repeatedly makes small, synchronous HTTP requests."""
    successful_requests = 0
    for i in range(iterations):
        try:
            # Making a request forces a DNS lookup (initially), TCP handshake,
            # data transfer, and connection teardown—all of which consume power.
            response = httpx.get(target_url, timeout=5)
            # Just checking the status ensures the full cycle completed
            _ = response.status_code
            successful_requests += 1

        except httpx.HTTPError as e:
            # Handle connection errors gracefully without stopping the benchmark
            print(f"  Warning: Request failed on iteration {i + 1} ({e.__class__.__name__})")

        time.sleep(0.1)  # Add a small delay to avoid getting rate limited
    return successful_requests
