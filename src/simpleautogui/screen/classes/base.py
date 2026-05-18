import math
from time import sleep, time
from typing import Iterable

import keyboard
import mouse
import numpy as np
import pyautogui as pg
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageGrab

from simpleautogui.notify import Notify
from simpleautogui.screen.utils import parse_color


class Point:
    def __init__(self, x: int = None, y: int = None):
        if x is None or y is None:
            current_position = pg.position()
            x = current_position.x if x is None else x
            y = current_position.y if y is None else y
        self.x = x
        self.y = y

    def __str__(self):
        return f'Point(x={self.x}, y={self.y})'

    def __repr__(self):
        return self.__str__()

    def to_tuple(self) -> tuple[int, int]:
        return self.x, self.y

    def click(self, o_x: int = 0, o_y: int = 0, **click_kwargs) -> None:
        """
        Wrapper on pyautogui.click().

        :param o_x: The offset added to the x-coordinate.
        :param o_y: The offset added to the y-coordinate.
        :param click_kwargs: Additional keyword arguments for pyautogui.click().
        """
        pg.click(self.x + o_x, self.y + o_y, **click_kwargs)

    def move_in(self, o_x: int = 0, o_y: int = 0, **move_kwargs) -> None:
        """
        Moves the mouse cursor to the point.

        :param o_x: The offset added to the x-coordinate.
        :param o_y: The offset added to the y-coordinate.
        :param move_kwargs: Additional keyword arguments for pyautogui.moveTo().
        """
        pg.moveTo(self.x + o_x, self.y + o_y, **move_kwargs)

    def drag_to(self, to_point: 'Point', **drag_kwargs) -> None:
        """
        Drags from the current point and drops to a target point.
        """
        self.move_in()
        pg.dragTo(to_point.x, to_point.y, **drag_kwargs)

    def drag_rel(self, rel_x: int, rel_y: int, **drag_kwargs) -> None:
        """
        Drags from the current point with offset to a relative position.
        """
        self.move_in()
        pg.dragRel(rel_x, rel_y, **drag_kwargs)

    @property
    def color(self) -> tuple[int, int, int]:
        return pg.pixel(self.x, self.y)

    @staticmethod
    def input(button='right', timeout=10) -> 'Point':
        """
        Waits for a mouse click or keyboard button press and returns the cursor position.

        :param button: The mouse button or keyboard key to listen for.
        :param timeout: Time in seconds after which TimeoutError is raised.
        """
        start_time = time()
        while True:
            if timeout and time() - start_time > timeout:
                raise TimeoutError(f'input button={button} timeout.')

            if button in ('left', 'right', 'middle') and mouse.is_pressed(button):
                position = pg.position()
                return Point(position.x, position.y)

            if keyboard.is_pressed(button):
                position = pg.position()
                return Point(position.x, position.y)

            sleep(0.01)

    @staticmethod
    def get_distance(with_sign: bool = True, sleep_after_first: float | int = 0.2) -> float:
        """
        Waits for two mouse clicks and returns the distance between the points.

        :param with_sign: Deprecated compatibility argument. Distance is always non-negative.
        :param sleep_after_first: Sleep seconds after first click.
        """
        point1 = Point().input()
        sleep(sleep_after_first)
        point2 = Point().input()

        dx = point2.x - point1.x
        dy = point2.y - point1.y
        return math.sqrt(dx ** 2 + dy ** 2)

    @staticmethod
    def get_deviation(with_sign: bool = True, sleep_after_first: float | int = 0.2) -> tuple[int, int]:
        """
        Waits for two mouse clicks and returns the deviation in X and Y coordinates.

        :param with_sign: If True, returns deviation with sign. If False, returns absolute deviation.
        :param sleep_after_first: Sleep seconds after first click.
        """
        point1 = Point().input()
        sleep(sleep_after_first)
        point2 = Point().input()
        if not all((point1, point2)):
            raise TimeoutError('Unable to read two points.')

        deviation_x = point2.x - point1.x
        deviation_y = point2.y - point1.y

        if with_sign:
            return deviation_x, deviation_y
        return abs(deviation_x), abs(deviation_y)

    @staticmethod
    def remove_proximity(points: Iterable['Point'], proximity_threshold_px: int) -> list['Point']:
        """
        Filters out points that are within a certain proximity threshold.
        """
        result = []
        for point in points:
            if not any(
                    abs(point.x - saved_point.x) <= proximity_threshold_px
                    and abs(point.y - saved_point.y) <= proximity_threshold_px
                    for saved_point in result
            ):
                result.append(point)
        return result


class Region:
    """
    Represents a rectangular area on the screen.
    """

    def __init__(
            self,
            x: int = 0,
            y: int = 0,
            w: int = None,
            h: int = None
    ):
        screen_size = pg.size()
        self.x = x
        self.y = y
        self.w = screen_size.width if w is None else w
        self.h = screen_size.height if h is None else h
        self.cx = self.x + self.w // 2
        self.cy = self.y + self.h // 2

    def __str__(self):
        return f'Region(x={self.x}, y={self.y}, w={self.w}, h={self.h}, cx={self.cx}, cy={self.cy})'

    def __repr__(self):
        return self.__str__()

    def show(self):
        """
        Shows region by Pillow.show() method.
        """
        self.screenshot().show()

    def to_tuple(self) -> tuple[int, int, int, int]:
        return self.x, self.y, self.w, self.h

    def screenshot(self):
        return pg.screenshot(region=self.to_tuple())

    def find_text(
            self,
            text: str,
            lang: str = 'eng+rus',
            contrast: int | float = 0,
            resize: int | float = 0,
            sharpen: bool = True,
            case_sensitive: bool = False,
            min_confidence: int = 80,
            **image_to_data_kwargs
    ) -> list['Region']:
        """
        Searches text within the region using OCR and returns matching regions.
        """
        image, scale = self._preprocess_image(
            self.screenshot(),
            contrast=contrast,
            resize=resize,
            sharpen=sharpen,
        )
        data = pytesseract.image_to_data(
            image,
            lang=lang,
            output_type=pytesseract.Output.DICT,
            **image_to_data_kwargs,
        )
        search_text = self._normalize_text(text, case_sensitive)
        if not search_text:
            return []

        regions = []
        line_items = {}
        for index in range(len(data['text'])):
            detected_text = data['text'][index].strip()
            if not detected_text or self._read_confidence(data['conf'][index]) < min_confidence:
                continue

            item = {
                'text': detected_text,
                'left': self._data_value(data, 'left', index),
                'top': self._data_value(data, 'top', index),
                'width': self._data_value(data, 'width', index),
                'height': self._data_value(data, 'height', index),
            }

            if self._normalize_text(detected_text, case_sensitive) == search_text:
                regions.append(self._bbox_region(self, [item], scale))

            line_items.setdefault(self._line_key(data, index), []).append(item)

        if ' ' in search_text:
            for items in line_items.values():
                line_text = self._normalize_text(' '.join(item['text'] for item in items), case_sensitive)
                if search_text in line_text:
                    regions.append(self._bbox_region(self, items, scale))

        return self.remove_proximity(regions)

    def text(
            self,
            lang: str = 'eng+rus',
            contrast: int | float = 0,
            resize: int | float = 0,
            sharpen: bool = True,
            **image_to_string_kwargs
    ) -> str:
        """
        Recognizes and returns text in the specified screen region.
        """
        image, _ = self._preprocess_image(
            self.screenshot(),
            contrast=contrast,
            resize=resize,
            sharpen=sharpen,
        )
        return pytesseract.image_to_string(image, lang=lang, **image_to_string_kwargs)

    def click(self, center: bool = True, o_x: int = 0, o_y: int = 0, **click_kwargs) -> None:
        """
        Performs a mouse click on the region.
        """
        Point(
            self.cx + o_x if center else self.x + o_x,
            self.cy + o_y if center else self.y + o_y,
        ).click(**click_kwargs)

    def move_in(self, center: bool = True, o_x: int = 0, o_y: int = 0, **move_kwargs) -> None:
        """
        Moves the mouse cursor in the region.
        """
        move_x = self.cx + o_x if center else self.x + o_x
        move_y = self.cy + o_y if center else self.y + o_y
        pg.moveTo(move_x, move_y, **move_kwargs)

    def drag_to(self, to: Point, center: bool = True, o_x: int = 0, o_y: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current region and drops to a target point.
        """
        (Point(self.cx, self.cy) if center else Point(self.x, self.y)).move_in(o_x, o_y)
        pg.dragTo(to.x, to.y, **drag_kwargs)

    def drag_rel(
            self,
            rel_x: int,
            rel_y: int,
            center: bool = True,
            o_x: int = 0,
            o_y: int = 0,
            **drag_kwargs
    ) -> None:
        """
        Drags from the current region to a relative position.
        """
        (Point(self.cx, self.cy) if center else Point(self.x, self.y)).move_in(o_x, o_y)
        pg.dragRel(rel_x, rel_y, **drag_kwargs)

    @staticmethod
    def remove_proximity(regions: Iterable['Region'], proximity_threshold_px: int = 10) -> list['Region']:
        """
        Filters out regions that are within a certain proximity threshold.
        """
        result = []
        for region in regions:
            if not any(
                    abs(region.x - saved_region.x) <= proximity_threshold_px
                    and abs(region.y - saved_region.y) <= proximity_threshold_px
                    for saved_region in result
            ):
                result.append(region)
        return result

    def wait_image(
            self,
            paths: str | tuple[str, ...] | list[str],
            timeout: int | float = 10,
            confidence: float = 0.9,
            error_dialog: bool = False,
            check_interval: int | float = 0.1
    ) -> 'Region' | None:
        """
        Waits for a specified image or images to appear in the region.
        """
        image_paths = self._normalize_paths(paths)
        end_time = time() + timeout
        first_check = True
        while first_check or time() < end_time:
            first_check = False
            for path in image_paths:
                try:
                    box = pg.locateOnScreen(path, confidence=confidence, region=self.to_tuple())
                    if box is not None:
                        return self._box_to_region(box)
                except pg.ImageNotFoundException:
                    pass

            if timeout == 0:
                return None
            sleep(check_interval)

        if error_dialog and not Notify.continue_or_stop(f'Images not found: {", ".join(image_paths)}'):
            raise pg.ImageNotFoundException
        return None

    def wait_images(
            self,
            paths: str | tuple[str, ...] | list[str],
            timeout: int | float = 10,
            confidence: float = 0.9,
            error_dialog: bool = False,
            check_interval: int | float = 0.1,
            proximity_threshold_px: int = 2,
            min_matches: int = 1
    ) -> list['Region']:
        """
        Waits for multiple images to appear in the region.
        """
        image_paths = self._normalize_paths(paths)
        end_time = time() + timeout
        boxes = []
        first_check = True
        while first_check or time() < end_time:
            first_check = False
            for path in image_paths:
                try:
                    boxes = [
                        self._box_to_region(box)
                        for box in pg.locateAllOnScreen(path, confidence=confidence, region=self.to_tuple())
                    ]
                    boxes = self.remove_proximity(boxes, proximity_threshold_px)
                    if min_matches and len(boxes) >= min_matches:
                        return boxes
                    if boxes:
                        continue
                except pg.ImageNotFoundException:
                    pass

            if timeout == 0:
                break
            sleep(check_interval)

        if boxes and min_matches == 0:
            return boxes
        if error_dialog and not Notify.continue_or_stop(f'Images not found: {", ".join(image_paths)}'):
            raise pg.ImageNotFoundException
        return []

    def wait_color(
            self,
            color: str | tuple[int, int, int] | list[int],
            timeout: int | float = 10,
            confidence: float = 0.9,
            error_dialog: bool = False,
            check_interval: int | float = 0.1
    ) -> Point | None:
        """
        Waits for a specified color to appear in the region.
        """
        rgb_color = parse_color(color)
        end_time = time() + timeout
        first_check = True
        while first_check or time() < end_time:
            first_check = False
            found, point = self.check_color(self._screenshot_array(), rgb_color, confidence)
            if found:
                return Point(point.x + self.x, point.y + self.y)

            if timeout == 0:
                break
            sleep(check_interval)

        if error_dialog and not Notify.continue_or_stop(f'Color not found: {rgb_color}'):
            raise TimeoutError(f'Color not found: {rgb_color}')
        return None

    def wait_colors(
            self,
            color: str
                   | tuple[int, int, int]
                   | list[int]
                   | tuple[str | tuple[int, int, int], ...]
                   | list[str | tuple[int, int, int]],
            timeout: int | float = 10,
            confidence: float = 0.9,
            error_dialog: bool = False,
            check_interval: int | float = 0.1,
            proximity_threshold_px: int = 2,
            min_matches: int = 0
    ) -> list[Point] | None:
        """
        Waits for colors to appear in the region.

        If min_matches is 0, returns all matches from the first screenshot with matches.
        """
        colors = self._normalize_colors(color)
        end_time = time() + timeout
        first_check = True
        while first_check or time() < end_time:
            first_check = False
            matches = self._find_colors(self._screenshot_array(), colors, confidence)
            matches = [Point(point.x + self.x, point.y + self.y) for point in matches]
            matches = Point.remove_proximity(matches, proximity_threshold_px)
            if min_matches and len(matches) >= min_matches:
                return matches
            if matches and min_matches == 0:
                return matches

            if timeout == 0:
                break
            sleep(check_interval)

        if error_dialog:
            Notify.continue_or_stop(f'Colors not found: {colors}')
        return None

    @staticmethod
    def _preprocess_image(image, contrast: int | float = 0, resize: int | float = 0, sharpen: bool = True):
        scale = float(resize) if resize else 1.0
        if scale <= 0:
            raise ValueError('resize must be greater than 0')
        if resize:
            image = image.resize([int(scale * size) for size in image.size], Image.LANCZOS)
        if contrast:
            image = ImageEnhance.Contrast(image).enhance(contrast)
        if sharpen:
            image = image.filter(ImageFilter.SHARPEN)
        return image, scale

    @staticmethod
    def _read_confidence(value) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return -1

    @staticmethod
    def _normalize_text(value: str, case_sensitive: bool) -> str:
        value = value.strip()
        return value if case_sensitive else value.lower()

    @staticmethod
    def _data_value(data, name: str, index: int):
        if name in data:
            return data[name][index]
        legacy_name = {'width': 'w', 'height': 'h'}.get(name)
        if legacy_name in data:
            return data[legacy_name][index]
        raise KeyError(name)

    @staticmethod
    def _line_key(data, index: int) -> tuple:
        def value(name, fallback):
            values = data.get(name)
            if values is None:
                return fallback
            return values[index]

        return (
            value('block_num', 0),
            value('par_num', 0),
            value('line_num', index),
        )

    @staticmethod
    def _bbox_region(region: 'Region', items: list[dict], scale: float) -> 'Region':
        left = min(item['left'] for item in items) / scale
        top = min(item['top'] for item in items) / scale
        right = max(item['left'] + item['width'] for item in items) / scale
        bottom = max(item['top'] + item['height'] for item in items) / scale
        return Region(
            int(round(region.x + left)),
            int(round(region.y + top)),
            int(round(right - left)),
            int(round(bottom - top)),
        )

    @staticmethod
    def _box_to_region(box) -> 'Region':
        width = getattr(box, 'width', getattr(box, 'w', None))
        height = getattr(box, 'height', getattr(box, 'h', None))
        return Region(box.left, box.top, width, height)

    @staticmethod
    def _normalize_paths(paths: str | tuple[str, ...] | list[str]) -> list[str]:
        image_paths = [paths] if isinstance(paths, str) else list(paths)
        if not image_paths:
            raise ValueError('At least one image path must be provided.')
        return image_paths

    @staticmethod
    def _color_bounds(color: tuple[int, int, int], confidence: float) -> tuple[np.ndarray, np.ndarray]:
        if confidence < 0 or confidence > 1:
            raise ValueError('confidence must be between 0 and 1')
        tolerance = int(round(255 * (1 - confidence)))
        color_array = np.array(color, dtype=np.int16)
        lower_bound = np.clip(color_array - tolerance, 0, 255).astype(np.uint8)
        upper_bound = np.clip(color_array + tolerance, 0, 255).astype(np.uint8)
        return lower_bound, upper_bound

    def _screenshot_array(self) -> np.ndarray:
        screenshot = ImageGrab.grab(bbox=(self.x, self.y, self.x + self.w, self.y + self.h))
        return np.array(screenshot.convert('RGB'))

    @classmethod
    def check_color(cls, image: np.ndarray, color: tuple[int, int, int], confidence: float):
        lower_bound, upper_bound = cls._color_bounds(color, confidence)
        mask = np.all((image >= lower_bound) & (image <= upper_bound), axis=2)
        points = np.argwhere(mask)
        if len(points) > 0:
            y, x = points[0]
            return True, Point(int(x), int(y))
        return False, None

    @staticmethod
    def _normalize_colors(
            color: str
                   | tuple[int, int, int]
                   | list[int]
                   | tuple[str | tuple[int, int, int], ...]
                   | list[str | tuple[int, int, int]]
    ) -> list[tuple[int, int, int]]:
        if isinstance(color, str):
            return [parse_color(color)]
        if (
                isinstance(color, (tuple, list))
                and len(color) == 3
                and all(isinstance(channel, int) for channel in color)
        ):
            return [parse_color(color)]
        return [parse_color(item) for item in color]

    @classmethod
    def _find_colors(
            cls,
            image: np.ndarray,
            colors: list[tuple[int, int, int]],
            confidence: float
    ) -> list[Point]:
        result = []
        for color in colors:
            lower_bound, upper_bound = cls._color_bounds(color, confidence)
            mask = np.all((image >= lower_bound) & (image <= upper_bound), axis=2)
            for y, x in np.argwhere(mask):
                result.append(Point(int(x), int(y)))
        return result
