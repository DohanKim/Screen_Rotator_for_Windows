import win32api as win32
import win32con
import sys
import os
from pynput.keyboard import Key, KeyCode, Listener
from infi.systray import SysTrayIcon

def set_display_orientation(orientation):
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
        device = win32.EnumDisplayDevices(None, 0)
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

    print("Keys pressed:", pressed_keys)

    combination_to_orientation = {
        frozenset([Key.ctrl_l, Key.alt_l, Key.up]): 0,
        frozenset([Key.ctrl_l, Key.alt_l, Key.right]): 90,
        frozenset([Key.ctrl_l, Key.alt_l, Key.down]): 180,
        frozenset([Key.ctrl_l, Key.alt_l, Key.left]): 270,
    }

    for combination, orientation in combination_to_orientation.items():
        if is_combination_pressed(combination):
            print("Set orientation to", orientation, "degree")
            set_display_orientation(orientation)

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
        set_display_orientation(0)
        listener.stop()

    menu_options = (
        ("(0) Landscape", None, lambda s: set_display_orientation(0)),
        ("(90) Portrait", None, lambda s: set_display_orientation(90)),
        ("(180) Flipped Landscape", None, lambda s: set_display_orientation(180)),
        ("(270) Flipped Portrait", None, lambda s: set_display_orientation(270)),
    )
    systray = SysTrayIcon(resource_path("rotate.ico"), "Screen Rotator", menu_options, on_quit=exit_listener)
    systray.start()

# pyinstaller main.spec
