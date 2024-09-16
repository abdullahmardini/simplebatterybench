#!/usr/bin/env python3
'''
stfu pylint
'''

import subprocess
import time
import functools
import re
import psutil


def get_battery_energy():
    '''
    Would also be nice to know how much Wh the thing currently has
    '''
    energy = None
    try:
        output = subprocess.check_output(['upower', '-i', '/org/freedesktop/UPower/devices/battery_BAT0'])
        lines = output.decode('utf-8').split('\n')
        for line in lines:
            if 'energy:' in line:
                energy = float(line.split(':')[1].strip().split()[0])
        return energy
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


def get_battery_level():
    '''
    Returns the current battery level in percent
    '''
    battery = psutil.sensors_battery()
    if battery is None:
        print("No battery found or can't ready battery level...")
        exit(1)
    return battery.percent


def measure_battery_life(func):
    '''
    Just tells us how much battery we spend during stuff
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        initial_battery = get_battery_level()
        initial_energy = get_battery_energy()
        result = func(*args, **kwargs)
        final_battery = get_battery_level()
        final_energy = get_battery_energy()
        print(f"Battery life spent: {initial_battery - final_battery}%")
        print(f"Power spent: {initial_energy - final_energy}Wh")
        return result
    return wrapper


def quick_bench(time_secs):
    '''
    quick and dirty benchmark. not a good measure for latency
    and probably the other things you care about when running
    on battery
    '''
    command = ["sysbench", "--threads=8", f"--time={time_secs}", "cpu", "run"]
    output = subprocess.check_output(command, universal_newlines=True)

    pattern = r"events per second: (\d+\.\d+)"
    match = re.search(pattern, output)
    if match:
        return float(match.group(1))
    else:
        return None


def quick_sleep(time_secs):
    '''
    this one needs root, until i figure out something else
    uses this rtc wake business to sleep
    '''
    command = ["rtcwake", "-m", "freeze", "-s", str(time_secs)]
    subprocess.check_call(command)


@measure_battery_life
def sleep_check(test_time):
    '''
    checks battery drain during sleep
    '''
    quick_sleep(test_time)


@measure_battery_life
def wake_check(test_time):
    '''
    checks battery drain during use.
    This is .... kind of a crappy test.
    My idea is that the typical developer will spend most of their
    time using an electron app or two (and they will probably crash)
    in addition to a browser and probably docker. This should have
    a moderate energy impact, coupled with the occassional high
    impact energy usage, like say compiling.
    So what I want to do is restrict the amount of time we benchmark
    and otherwise just sit idle, which will possibly replicate just
    staring at vscode and thinking about the problem??? who knows
    '''
    bench_time = test_time // 5
    wait_time = (4 * test_time ) // 5
    score = quick_bench(bench_time)
    time.sleep(wait_time)
    print(f"perf score of {score}")


def main():
    '''
    apparently I may be the first person to try benchmarking battery life in linux
    i want to know which offers the best savings: tlp vs tuned vs ppd
    in a quantifiable way instead of which "feels" better or complaining about some
    arbitrary parameter like oh it's a shell script and that's bad because i
    worship object oriented bullshit
    '''
    test_time = 60
    # sleep_check(test_time)
    wake_check(test_time)


if __name__ == "__main__":
    main()
