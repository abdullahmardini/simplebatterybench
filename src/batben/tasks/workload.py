"""
This is just a playbed for some synthetic benchmark ideas.
The goals are (in order):
1. deterministic
2. scorable
3. indicative of real world performance

on a side note, i now realize why writing something like a geekbench clone is really hard
maybe I SHOULD just ise geekbench (or a clone).
"""

import time
import cpu_task


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


@events_per_second("CPU")
def cpu_task(num_primes: int = 500) -> int:
    count = 0
    for i in range(2, num_primes):
        if cpu_task.is_prime(i):
            count += 1
    return count
