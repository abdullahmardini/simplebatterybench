#!/usr/bin/env python3
'''
stfu pylint
'''

import subprocess
import re
import psutil

def get_battery_level():
    '''
    Returns the current battery level in percent
    '''
    battery = psutil.sensors_battery()
    if battery is None:
        print("No battery found or can't ready battery level...")
        exit(1)
    return battery.percent

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


def sleep_check(test_time):
    '''
    checks battery drain during sleep
    '''
    initial_battery = get_battery_level()
    quick_sleep(test_time)
    final_battery = get_battery_level()
    delta_battery = initial_battery - final_battery
    print(f"slept for {test_time} seconds and spent {delta_battery}%")


def wake_check(test_time):
    '''
    checks battery drain during use
    '''
    initial_battery = get_battery_level()
    score = quick_bench(test_time)
    final_battery = get_battery_level()
    delta_battery = initial_battery - final_battery
    print(f"perf score of {score} and spent {delta_battery}%")


def main():
    '''
    apparently I may be the first person to try benchmarking battery life in linux
    i want to know which offers the best savings: tlp vs tuned vs ppd
    in a quantifiable way instead of which "feels" better or complaining about some
    arbitrary parameter like oh it's a shell script and that's bad because i
    worship object oriented bullshit
    '''
    initial_battery_level = get_battery_level()

    print(f"Initial battery level: {initial_battery_level}%")

    test_time = 300
    sleep_check(test_time)
    wake_check(test_time)

    final_battery_level = get_battery_level()
    print(f"Final battery level: {final_battery_level}%")

    battery_drain = initial_battery_level - final_battery_level
    print(f"Battery drain: {battery_drain}%")

if __name__ == "__main__":
    main()
