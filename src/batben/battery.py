import functools
import time

import psutil
from pydbus import SystemBus


def _get_battery_energy() -> float:
    """
    Gets the current battery energy (in Wh) by querying the UPower D-Bus service.
    """
    bus = SystemBus()

    try:
        battery = bus.get("org.freedesktop.UPower", "/org/freedesktop/UPower/devices/battery_BAT0")
    except Exception as e:
        print(f"Error accessing D-Bus object. Is this a laptop?\n    {e}")
        return 0.0

    return battery.Energy  # energy_wh


def _get_battery_level() -> float:
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
        initial_battery = _get_battery_level()
        initial_energy = _get_battery_energy()
        result = func(*args, **kwargs)
        final_time = time.time()
        final_battery = _get_battery_level()
        final_energy = _get_battery_energy()
        if final_energy > initial_energy:
            print("Energy increased during this period... Did you plug in your laptop?")
        print(f"Battery life spent: {initial_battery - final_battery:.1f}%")
        elapsed_time = final_time - initial_time
        print(f"Power spent: {initial_energy - final_energy:.1f}Wh")
        print(f"Elapsed time: {elapsed_time:.1f}")
        return result

    return wrapper
