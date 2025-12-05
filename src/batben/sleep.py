from pydbus import SystemBus
from datetime import datetime, timedelta


def quick_sleep_dbus(time_secs: int) -> None:
    """
    Suspends the system and sets a scheduled wakeup time via systemd-logind
    using D-Bus, avoiding the need for rtcwake and subprocess.

    NOTE: This requires the calling user to be allowed to suspend/hibernate,
          usually via polkit/sudoers configuration, but avoids full root for D-Bus.
    Example usage (uncomment to test):
    quick_sleep_dbus(600) # Sleep for 10 minutes (600 seconds)
    """
    bus = SystemBus()

    manager = bus.get("org.freedesktop.login1", "/org/freedesktop/login1")

    now = datetime.now()
    wakeup_time = now + timedelta(seconds=time_secs)
    wakeup_us = int(wakeup_time.timestamp() * 1000000)
    manager.SetWakeup("suspend", wakeup_us)
    manager.Suspend(False)
