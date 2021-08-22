import win32api as win32
import win32con
import sys
import os
from pynput.keyboard import Key, KeyCode, Listener
from infi.systray import SysTrayIcon

def get_display_names():
    monitors = win32.EnumDisplayMonitors()
    display_names = []
    for monitor in monitors:
        monitor_info = win32.GetMonitorInfo(monitor[0])
        device_name = win32.EnumDisplayDevices(monitor_info['Device'], 0).DeviceString
        display_names.append(device_name)
    return display_names

device_num = 0

def set_device_num(num):
    global device_num
    device_num = num

def set_display_orientation(orientation, device_num = 0):
    orientation_to_enum = {
        0: win32con.DMDO_DEFAULT,
        90: win32con.DMDO_270,
        180:  win32con.DMDO_180,
        270: win32con.DMDO_90
    }
    orientation_enum = orientation_to_enum.get(orientation)

    if orientation_enum == None:
        print ("provide proper orientation in degree: 0, 90, 180, 270")
    else:
        device = win32.EnumDisplayDevices(None, device_num)
        setting = win32.EnumDisplaySettings(device.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
        if((setting.DisplayOrientation + orientation_enum) % 2 == 1):
            setting.PelsWidth, setting.PelsHeight = setting.PelsHeight, setting.PelsWidth
        setting.DisplayOrientation = orientation_enum

        win32.ChangeDisplaySettingsEx(device.DeviceName,setting)

# The currently pressed keys
pressed_keys = set()

def is_combination_pressed(combination):
    return (combination - pressed_keys) == set()

def on_press(key):
    pressed_keys.add(key)

    combination_to_orientation = {
        frozenset([Key.ctrl_l, Key.alt_l, Key.up]): 0,
        frozenset([Key.ctrl_l, Key.alt_r, Key.up]): 0,
        frozenset([Key.ctrl_r, Key.alt_l, Key.up]): 0,
        frozenset([Key.ctrl_r, Key.alt_r, Key.up]): 0,
        frozenset([Key.ctrl_l, Key.alt_l, Key.right]): 90,
        frozenset([Key.ctrl_l, Key.alt_r, Key.right]): 90,
        frozenset([Key.ctrl_r, Key.alt_l, Key.right]): 90,
        frozenset([Key.ctrl_r, Key.alt_r, Key.right]): 90,
        frozenset([Key.ctrl_l, Key.alt_l, Key.down]): 180,
        frozenset([Key.ctrl_l, Key.alt_r, Key.down]): 180,
        frozenset([Key.ctrl_r, Key.alt_l, Key.down]): 180,
        frozenset([Key.ctrl_r, Key.alt_r, Key.down]): 180,
        frozenset([Key.ctrl_l, Key.alt_l, Key.left]): 270,
        frozenset([Key.ctrl_l, Key.alt_r, Key.left]): 270,
        frozenset([Key.ctrl_r, Key.alt_l, Key.left]): 270,
        frozenset([Key.ctrl_r, Key.alt_r, Key.left]): 270,
    }

    for combination, orientation in combination_to_orientation.items():
        if is_combination_pressed(combination):
            print("Set orientation to", orientation, "degree")
            set_display_orientation(orientation, device_num)

def on_release(key):
    pressed_keys.discard(key)

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    listener = Listener(on_press=on_press, on_release=on_release)
    listener.start()
    def exit_listener(sysTrayIcon):
        set_display_orientation(0, device_num)
        listener.stop()

    def display_options():
        display_names = get_display_names()
        options = []
        for i, display_name in enumerate(display_names):
            icon = None
            if device_num == i:
                icon = resource_path("checked.ico")
            options.append((str(i+1) + ". " + display_name, icon, lambda s: set_device_num(i)))
        return tuple(options)

    menu_options = (
        ("Choose Display", None, display_options()),
        ("(0) Landscape", None, lambda s: set_display_orientation(0, device_num)),
        ("(90) Portrait", None, lambda s: set_display_orientation(90, device_num)),
        ("(180) Flipped Landscape", None, lambda s: set_display_orientation(180, device_num)),
        ("(270) Flipped Portrait", None, lambda s: set_display_orientation(270, device_num)),
    )
    systray = SysTrayIcon(resource_path("rotate.ico"), "Screen Rotator", menu_options, on_quit=exit_listener)
    systray.start()

# pyinstaller main.py --onefile --hidden-import=pkg_resources --windowed --add-data checked.ico;. --add-data rotate.ico;.
