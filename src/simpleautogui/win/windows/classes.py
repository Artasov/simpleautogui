import win32api
import win32con
import win32gui

from simpleautogui import Region
from simpleautogui.win.windows.exceptions.base import DisplayMonitorEnumerationError


class Window:
    def __init__(self, hwnd=None, title=None):
        """
        Initializes the window object. Can be initialized with a window handle (hwnd) or title.
        If title is provided, it doesn't need to be complete, a substring of the title is sufficient.
        If multiple windows match the title, the first one found is used.
        Raises WindowNotFound exception if the window cannot be identified by hwnd or title.

        :param hwnd: The handle of the window.
        :param title: The title or substring of the window title.
        """
        self.hwnd = None

        if hwnd:
            self.hwnd = hwnd
        elif title:
            hwnds = self.byTitle(title)
            if hwnds:
                self.hwnd = hwnds[0]

    def __str__(self):
        return f'Window(\'{self.title}\')'

    def __repr__(self):
        return f'Window(\'{self.title}\')'

    @property
    def title(self) -> str:
        """
        Retrieves the window's title using its handle.
        """
        return win32gui.GetWindowText(self.hwnd)

    @property
    def region(self):
        """
        Returns a Region object with the coordinates and dimensions of the window.
        """
        rect = win32gui.GetWindowRect(self.hwnd)
        x, y = rect[0], rect[1]
        w, h = rect[2] - x, rect[3] - y
        return Region(x, y, w, h)

    @classmethod
    def all(cls) -> list['Window']:
        """
        Returns a list of all visible windows with titles as Window objects.
        """

        def callback(hwnd, hwnd_list):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                hwnd_list.append(cls(hwnd))

        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows

    @classmethod
    def byTitle(cls, title, case_sensitive: bool = False) -> list:
        """
        Finds windows by a partial match of their title and returns a list of Window objects.
        The search can be case-sensitive or insensitive.

        :param title: The title or substring of the window title.
        :param case_sensitive: If True, the search will be case-sensitive.
        :return: A list of Window objects with titles matching the substring.
        """

        def callback(hwnd, hwnd_list):
            window_title = win32gui.GetWindowText(hwnd)
            if case_sensitive:
                if title in window_title:
                    hwnd_list.append(hwnd)
            else:
                if title.lower() in window_title.lower():
                    hwnd_list.append(hwnd)

        hwnd_list_ = []
        win32gui.EnumWindows(callback, hwnd_list_)
        return [cls(hwnd=hwnd) for hwnd in hwnd_list_]

    def setGeometry(self, x=None, y=None, w=None, h=None, safe: bool = True):
        """
        Changes the size and position of the window. If any arguments are not provided, those dimensions are not changed.

        :param x: The x position of the window.
        :param y: The y position of the window.
        :param w: The w of the window.
        :param h: The h of the window.
        :param safe: if True raising before change geometry.
        """
        if safe: self.raiseIt()

        rect = win32gui.GetWindowRect(self.hwnd)
        x = x if x is not None else rect[0]
        y = y if y is not None else rect[1]
        w = w if w is not None else rect[2] - rect[0]
        h = h if h is not None else rect[3] - rect[1]
        win32gui.MoveWindow(self.hwnd, x, y, w, h, True)

    def raiseIt(self):
        """
        Brings the window to the front, attempting multiple times if necessary.
        """
        if win32gui.IsIconic(self.hwnd):
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    def maximize(self):
        """
        Maximizes the window.
        """
        win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)

    def minimize(self):
        """
        Minimizes the window.
        """
        win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)

    def restore(self, safe: bool = True):
        """
        Restores the window to normal size.
        :param safe: if True raising before restoring.
        """
        if safe:
            self.raiseIt()
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)

    def close(self):
        """
        Closes the window.
        """
        win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)


class Monitor:
    def __init__(self, name: str, fregion: Region, wregion: Region, flags: int, device: str):
        self.name = name
        self.fregion = fregion
        self.wregion = wregion
        self.flags = flags
        self.device = device

    @staticmethod
    def all() -> list['Monitor']:
        monitors_info = []
        try:
            for hMonitor, hdcMonitor, pyRect in win32api.EnumDisplayMonitors():
                monitors_info.append(win32api.GetMonitorInfo(hMonitor))
        except Exception:
            raise DisplayMonitorEnumerationError()

        monitors = []
        for index, monitor_info in enumerate(monitors_info):
            name = f"Monitor {index + 1}"
            monitor_rect = monitor_info['Monitor']
            work_rect = monitor_info['Work']
            flags = monitor_info['Flags']
            device = monitor_info['Device']

            monitors.append(
                Monitor(
                    name,
                    Region(monitor_rect[0], monitor_rect[1], monitor_rect[2], monitor_rect[3]),
                    Region(work_rect[0], work_rect[1], work_rect[2], work_rect[3]),
                    flags,
                    device))
        return monitors


class WindowsCluster:
    def __init__(self, windows: tuple[Window] | list[Window]):
        self.windows = windows

    def __str__(self):
        return 'WindowsCluster(\n    ' + ',\n    '.join(f'{window.title}' for window in self.windows) + '\n)'

    def __repr__(self):
        return self.__str__()

    def inGrid(self, rows: int, cols: int, region: Region):
        for index, window in enumerate(self.windows):
            region_w = region.w - region.x
            region_h = region.h - region.y

            window.restore()

            col = index % cols
            row = (index // cols) % rows

            x = region.x + col * region_w // cols
            y = region.y + row * region_h // rows
            w = region_w // cols + (region_w % cols > col)
            h = region_h // rows + (region_h % rows > row)

            window.setGeometry(x, y, w, h)
