#!/usr/bin/env python3

import subprocess
import time
import argparse
import functools
import psutil
import devsim


def get_battery_energy() -> float:
    """
    Would also be nice to know how much Wh the thing currently has
    """
    command = ["upower", "-i", "/org/freedesktop/UPower/devices/battery_BAT0"]
    output = subprocess.check_output(command)
    lines = output.decode("utf-8").split("\n")
    for line in lines:
        if "energy:" in line:
            return float(line.split(":")[1].strip().split()[0])
    exit(1)


def get_battery_level() -> float:
    """
    Returns the current battery level in percent
    """
    battery = psutil.sensors_battery()
    if battery is None:
        print("No battery found or can't ready battery level...")
        exit(1)
    return battery.percent


def measure_battery_life(func):
    """
    Decorator that tells us how much battery we spend during stuff
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        initial_time = time.time()
        initial_battery = get_battery_level()
        initial_energy = get_battery_energy()
        result = func(*args, **kwargs)
        final_time = time.time()
        final_battery = get_battery_level()
        final_energy = get_battery_energy()
        if final_energy > initial_energy:
            print("Energy increased during this period... Did you plug in your laptop?")
        print(f"Battery life spent: {initial_battery - final_battery:.1f}%")
        elapsed_time = final_time - initial_time
        print(f"Power spent: {initial_energy - final_energy:.1f}Wh")
        print(f"Elapsed time: {elapsed_time:.1f}")
        return result

    return wrapper


def quick_sleep(time_secs: int) -> None:
    """
    this one needs root, by linux design - not mine.
    uses rtc wake to sleep
    """
    command = ["rtcwake", "-m", "freeze", "-s", str(time_secs)]
    subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


@measure_battery_life
def sleep_check(test_time):
    """
    Checks battery drain during sleep
    Input time in seconds
    """
    quick_sleep(test_time)
    print("Sleep portion follows:")


@measure_battery_life
def wake_check(test_time: int) -> None:
    """
    Checks battery drain during use.
    Ultimately this is a synthetic test. My assumption is that most workloads will have some sustained but light use, followed with bursts of compute. I think as long as it's close enough, deterministic, and measurable, it should be good enough.
    """
    print("Running simulated workload...")
    devsim.dev_workload(test_time)


def main():
    """
    Simple script to measure battery impact of wake and sleep in some quantifiable way. This is intended to be a simple and rough heuristic.
    """
    parser = argparse.ArgumentParser(
        description="Simple battery benchmark to measure tuning impact on energy consumption"
    )
    parser.add_argument(
        "-t", "--time", type=int, default=60, help="Time in seconds to run the test"
    )
    parser.add_argument(
        "-s",
        "--sleep",
        action="store_true",
        default=False,
        help="Measure battery impact during sleep",
    )
    parser.add_argument(
        "-w",
        "--wake",
        action="store_true",
        default=True,
        help="Measure battery impact during use",
    )

    args = parser.parse_args()
    test_time = args.time

    if args.sleep:
        sleep_check(test_time)
    if args.wake:
        wake_check(test_time)


if __name__ == "__main__":
    main()
