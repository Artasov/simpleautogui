import win32api
from typing import List, Tuple

import win32com.client
import win32con
import win32gui


def set_window_geometry(name: str, show: bool = True,
                        window_type=win32con.HWND_NOTOPMOST,
                        x: int = 0, y: int = 0, w: int = 0, h: int = 0,
                        flags=win32con.SWP_ASYNCWINDOWPOS):
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    hwnd = win32gui.FindWindow(None, name)
    win32gui.SetWindowPos(hwnd, window_type, x, y, w, h, flags)
    if show:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)


def get_all_windows():
    """ Gets a list of all windows in the order they were created. """

    def enum_windows_proc(hwnd, hwnd_list):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            hwnd_list.append(hwnd)
        return True

    hwnd_list = []
    win32gui.EnumWindows(enum_windows_proc, hwnd_list)
    return hwnd_list


def search_windows_by_title(title_substr: str) -> List[int]:
    """
    Find all windows whose titles contain the substring title_sub_str.
    """

    def enum_windows_proc(hwnd, hwnd_list):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if title_substr in window_title:
                hwnd_list.append(hwnd)
        return True

    hwnd_list = []
    win32gui.EnumWindows(enum_windows_proc, hwnd_list)
    return hwnd_list


def arrange_windows_in_grid(hwnds: List[int], rows: int, cols: int, monitors: Tuple[int] = (1,)):
    task_panel_height = 45

    def get_monitors_info():
        monitors_info_result = []
        try:
            for hMonitor, hdcMonitor, pyRect in win32api.EnumDisplayMonitors():
                monitors_info_result.append(win32api.GetMonitorInfo(hMonitor))
            return monitors_info_result
        except Exception:
            print("Error while enumerating display monitors")
            return None

    monitors_info = get_monitors_info()
    selected_monitors = [monitors_info[int(i) - 1] for i in monitors if 0 < int(i) <= len(monitors_info)]

    for index, hwnd in enumerate(hwnds):
        monitor_index = index // (rows * cols) % len(selected_monitors)
        monitor_info = selected_monitors[monitor_index]['Monitor']
        screen_width = monitor_info[2] - monitor_info[0]
        screen_height = monitor_info[3] - monitor_info[1] - task_panel_height

        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        col = index % cols
        row = (index // cols) % rows

        x = monitor_info[0] + col * screen_width // cols
        y = monitor_info[1] + row * screen_height // rows
        width = screen_width // cols + (screen_width % cols > col)
        height = screen_height // rows + (screen_height % rows > row)

        # win32gui.MoveWindow(hwnd, x, y, width, height, True)
        win32gui.MoveWindow(hwnd, x - 5, y - 1, width + 15, height + 8, True)


def arrange_windows_in_grid_by_title(title_substr: str, rows: int, cols: int, monitors: Tuple[int]):
    all_hwnds = get_all_windows()
    hwnds = [hwnd for hwnd in all_hwnds if hwnd in search_windows_by_title(title_substr)]
    arrange_windows_in_grid(hwnds, rows, cols, monitors)

# Example usage
# arrange_windows_in_grid_by_title('YourWindowTitle', 2, 3, (1,))
