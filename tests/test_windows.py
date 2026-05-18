import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

try:
    from simpleautogui.screen.classes import base
    from simpleautogui.screen.classes.base import Region
    from simpleautogui.win.windows.classes import Monitor, Window, WindowsGrid
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(f'Missing optional test dependency: {exc.name}')


class FakeWindow:
    def __init__(self):
        self.geometry = None
        self.restored = False
        self.title = 'Fake'

    def restore(self):
        self.restored = True

    def set_geometry(self, x=None, y=None, w=None, h=None, safe=True):
        self.geometry = (x, y, w, h)


class WindowsTests(unittest.TestCase):
    def test_window_title_initialization_uses_found_hwnd(self):
        with patch.object(Window, 'by_title', return_value=[SimpleNamespace(hwnd=123)]):
            window = Window(title='Notepad')

        self.assertEqual(window.hwnd, 123)

    def test_monitor_rect_to_region_converts_to_size(self):
        with patch.object(base.pg, 'size', return_value=SimpleNamespace(width=1920, height=1080)):
            region = Monitor._rect_to_region((100, 200, 900, 800))

        self.assertEqual(region.to_tuple(), (100, 200, 800, 600))

    def test_windows_grid_arranges_using_region_size(self):
        windows = [FakeWindow(), FakeWindow(), FakeWindow(), FakeWindow()]
        with patch.object(base.pg, 'size', return_value=SimpleNamespace(width=1920, height=1080)):
            region = Region(100, 100, 800, 600)

        grid = WindowsGrid(windows=windows, rows=2, cols=2, region=region)
        grid.arrange()

        self.assertEqual(windows[0].geometry, (100, 100, 400, 300))
        self.assertEqual(windows[1].geometry, (500, 100, 400, 300))
        self.assertEqual(windows[2].geometry, (100, 400, 400, 300))
        self.assertEqual(windows[3].geometry, (500, 400, 400, 300))
        self.assertTrue(all(window.restored for window in windows))

    def test_windows_grid_rejects_overflow(self):
        windows = [FakeWindow(), FakeWindow(), FakeWindow()]
        with patch.object(base.pg, 'size', return_value=SimpleNamespace(width=1920, height=1080)):
            grid = WindowsGrid(windows=windows, rows=1, cols=2, region=Region(0, 0, 800, 600))

        with self.assertRaises(ValueError):
            grid.arrange()


if __name__ == '__main__':
    unittest.main()
