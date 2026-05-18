import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

try:
    import numpy as np
    from PIL import Image

    from simpleautogui.screen.classes import base
    from simpleautogui.screen.classes.base import Point, Region
    from simpleautogui.screen.utils import parse_color
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(f'Missing optional test dependency: {exc.name}')


class ScreenTests(unittest.TestCase):
    def test_point_keeps_zero_coordinate(self):
        with patch.object(base.pg, 'position', return_value=SimpleNamespace(x=42, y=43)):
            point = Point(0, None)

        self.assertEqual(point.to_tuple(), (0, 43))

    def test_region_default_size_is_read_at_initialization(self):
        with patch.object(base.pg, 'size', return_value=SimpleNamespace(width=1920, height=1080)):
            region = Region()

        self.assertEqual(region.to_tuple(), (0, 0, 1920, 1080))

    def test_parse_color_formats(self):
        self.assertEqual(parse_color('#0f0'), (0, 255, 0))
        self.assertEqual(parse_color('rgb(255, 0, 10)'), (255, 0, 10))
        self.assertEqual(parse_color('red'), (255, 0, 0))
        self.assertEqual(parse_color((1, 2, 3)), (1, 2, 3))

    def test_check_color_returns_first_matching_point(self):
        image = np.zeros((3, 4, 3), dtype=np.uint8)
        image[1, 2] = [10, 20, 30]

        found, point = Region.check_color(image, (10, 20, 30), confidence=1)

        self.assertTrue(found)
        self.assertEqual(point.to_tuple(), (2, 1))

    def test_wait_colors_returns_absolute_points(self):
        image = np.zeros((3, 4, 3), dtype=np.uint8)
        image[1, 2] = [10, 20, 30]

        with patch.object(base.pg, 'size', return_value=SimpleNamespace(width=1920, height=1080)):
            region = Region(100, 200, 4, 3)

        with patch.object(region, '_screenshot_array', return_value=image):
            points = region.wait_colors((10, 20, 30), timeout=0, confidence=1)

        self.assertEqual([point.to_tuple() for point in points], [(102, 201)])

    def test_find_text_scales_ocr_coordinates_back(self):
        data = {
            'text': ['Hello', 'World'],
            'conf': ['95.5', '93'],
            'left': [20, 34],
            'top': [20, 20],
            'width': [10, 10],
            'height': [10, 10],
            'block_num': [1, 1],
            'par_num': [1, 1],
            'line_num': [1, 1],
        }

        with patch.object(base.pg, 'size', return_value=SimpleNamespace(width=1920, height=1080)):
            region = Region(10, 20, 100, 50)

        with patch.object(region, 'screenshot', return_value=Image.new('RGB', (100, 50))):
            with patch.object(base.pytesseract, 'image_to_data', return_value=data):
                regions = region.find_text('Hello World', resize=2, sharpen=False)

        self.assertEqual(len(regions), 1)
        self.assertEqual(regions[0].to_tuple(), (20, 30, 12, 5))


if __name__ == '__main__':
    unittest.main()
