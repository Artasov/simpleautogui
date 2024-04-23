import win32api
import win32con
import win32gui

from simpleautogui import Region
from simpleautogui.win.windows.exceptions.base import (
    DisplayMonitorEnumerationError, IncorrectWindowInitialization,
    WindowByTitleNotFound, WindowSuchHwndDoesNotExist
)


class Window:
    def __init__(self, hwnd=None, title=None, index=0):
        """
        Initializes the window object. Can be initialized with a window handle (hwnd) or title.
        If title is provided, it doesn't need to be complete, a substring of the title is sufficient.

        :param hwnd: The handle of the window.
        :param title: The title or substring of the window title.
        :param index: If more than one window is found by title, the window object by index will be returned,
        the first(0) one by default.
        """
        self.hwnd = None

        if hwnd:
            self.hwnd = hwnd
            if not self.exists():
                raise WindowSuchHwndDoesNotExist(f'A window with this hwnd({self.hwnd}) does not exist.')
        elif title:
            hwnds = self.byTitle(title)
            if hwnds:
                self.hwnd = hwnds[index]
            else:
                raise WindowByTitleNotFound(f'Window with title \'{title}\' not found.')
        else:
            raise IncorrectWindowInitialization('hwnd= or title= parameter must be provided for Window initialization.')

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

    def exists(self, hwnd=None) -> bool:
        """
        Checks if a window exists by its hwnd.

        :param hwnd: The handle of the window to check.
        :return: True if the window exists, False otherwise.
        """
        return win32gui.IsWindow(hwnd or self.hwnd)

    def isVisible(self) -> bool:
        return win32gui.IsWindowVisible(self.hwnd)

    @classmethod
    def byTitle(cls, title, case_sensitive: bool = False) -> list['Window']:
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
        Changes the size and position of the window.
        If any arguments are not provided, those dimensions are not changed.

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

    @classmethod
    def all(cls) -> list['Monitor']:
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
                cls(
                    name=name,
                    fregion=Region(monitor_rect[0], monitor_rect[1], monitor_rect[2], monitor_rect[3]),
                    wregion=Region(work_rect[0], work_rect[1], work_rect[2], work_rect[3]),
                    flags=flags,
                    device=device
                )
            )
        return monitors


class WindowsGrid:
    def __init__(self,
                 windows: tuple[Window, ...] | list[Window, ...],
                 rows: int, cols: int,
                 region: Region = Region()
                 ):
        self.windows = list(windows)
        self.rows = rows
        self.cols = cols
        self.region = region

    def __str__(self):
        return 'WindowsGrid(\n    ' + ',\n    '.join(f'{window.title}' for window in self.windows) + '\n)'

    def __repr__(self):
        return self.__str__()

    def append(self, window: Window):
        """
        Appends a window to the list of windows and arranges them.
        """
        self.windows.append(window)
        self.arrange()

    def prepend(self, window: Window):
        """
        Prepends a window to the list of windows and arranges them.
        """
        self.windows.insert(0, window)
        self.arrange()

    def insert(self, index: int, window: Window):
        """
        Inserts a window into the list of windows at the specified index and arranges them.

        :param index: The index at which to insert the window.
        :param window: The window to insert.
        """
        self.windows.insert(index, window)
        self.arrange()

    def arrange(self):
        for index, window in enumerate(self.windows):
            region_w = self.region.w - self.region.x
            region_h = self.region.h - self.region.y

            window.restore()

            col = index % self.cols
            row = (index // self.cols) % self.rows

            x = self.region.x + col * region_w // self.cols
            y = self.region.y + row * region_h // self.rows
            w = region_w // self.cols + (region_w % self.cols > col)
            h = region_h // self.rows + (region_h % self.rows > row)

            window.setGeometry(x, y, w, h)
