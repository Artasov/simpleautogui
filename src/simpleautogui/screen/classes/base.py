import math
from time import time, sleep
from typing import Union

import cv2
import keyboard
import mouse
import numpy as np
import pyautogui as pg
import pytesseract
from PIL import Image, ImageGrab
from PIL import ImageEnhance, ImageFilter
from pyscreeze import pixelMatchesColor

from simpleautogui.base.classes.notify import Notify
from simpleautogui.screen.utils import hex_to_rgb


class Point:
    def __init__(self, x: int = None, y: int = None):
        self.clicked_position = None
        if not all((x, y)):
            current_position = pg.position()
            x = current_position.x if x is None else x
            y = current_position.y if y is None else y
        self.x = x
        self.y = y

    def __str__(self):
        return f'Point(x={self.x}, y={self.y})'

    def click(self, oX: int = 0, oY: int = 0, **click_kwargs) -> None:
        """
        Wrapper on pg.click().

        :param oX: The offset added to the x-coordinate.
        :param oY: The offset added to the y-coordinate.
        :param click_kwargs: Additional keyword arguments for pyautogui.click().
        """
        pg.click(self.x + oX, self.y + oY, **click_kwargs)

    def moveTo(self, oX: int = 0, oY: int = 0, **move_kwargs) -> None:
        """
        Moves the mouse cursor to the Point.
        :param oX: The offset added to the x-coordinate.
        :param oY: The offset added to the y-coordinate.
        :param move_kwargs: Additional keyword arguments for pyautogui.moveIn().
        """
        pg.moveTo(self.x + oX, self.y + oY, **move_kwargs)

    def dragTo(self, toPoint: 'Point', **drag_kwargs) -> None:
        """
        Drags from the current Point and drops to a target Point.
        """
        self.moveTo()
        pg.dragTo(toPoint.x, toPoint.y, **drag_kwargs)

    def dragRel(self, relX: int, relY: int, **drag_kwargs) -> None:
        """
        Drags from the current Point with offset to a relative position.
        """
        self.moveTo()
        pg.dragRel(relX, relY, **drag_kwargs)

    @property
    def color(self):
        pass

    @staticmethod
    def input(button='right', timeout=10) -> 'Point' | None:
        """
        Waits for a mouse click or keyboard button press and returns the cursor position.

        :param button: The mouse button or keyboard key to listen for. Default is 'left'.
        :param timeout: Time in seconds after which the method returns None if no input is detected.
        :return: Point object representing the cursor position or None if timeout is reached.
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
    def getDistance(with_sign: bool = True, sleep_after_first: float | int = 0.2) -> float:
        """
        Waits for two mouse clicks and returns the distance between the points.

        :param with_sign: If True, returns the distance considering the sign. If False, returns the absolute distance.
        :param sleep_after_first: Sleep seconds after first click.
        :return: Distance between the two points.
        """
        point1 = Point().input()
        sleep(sleep_after_first)
        point2 = Point().input()

        dx = point2.x - point1.x
        dy = point2.y - point1.y

        if with_sign:
            return math.sqrt(dx ** 2 + dy ** 2)
        else:
            return math.sqrt(abs(dx) ** 2 + abs(dy) ** 2)

    @staticmethod
    def getDeviation(with_sign: bool = True, sleep_after_first: float | int = 0.2) -> tuple[int, int]:
        """
        Waits for TWO mouse clicks and returns the deviation in X and Y coordinates.

        :param sleep_after_first: Sleep seconds after first click.
        :param with_sign: If True, returns the deviation with sign. If False, returns the absolute deviation.
        :return: A tuple (deviation_x, deviation_y) representing the deviation between the two points.
        """
        point1 = Point().input()
        sleep(sleep_after_first)
        point2 = Point().input()
        if not all((point1, point2)):
            raise

        deviation_x = point2.x - point1.x
        deviation_y = point2.y - point1.y

        if with_sign:
            return deviation_x, deviation_y
        else:
            return abs(deviation_x), abs(deviation_y)

    @staticmethod
    def removeProximity(points: list['Point'], proximity_threshold_px: int) -> list['Point']:
        """
        Filters out points that are within a certain proximity threshold.

        :param points: List of Point objects to filter.
        :param proximity_threshold_px: Pixel threshold for determining proximity.
        :return: List of filtered Point objects.
        """
        result = []
        for point in points:
            if not any(abs(point.x - p.x) <= proximity_threshold_px
                       and
                       abs(point.y - p.y) <= proximity_threshold_px
                       for p in result):
                result.append(point)
        return result


class Region:
    """
    Represents a rectangular area on the screen, providing methods to interact with it.

    :param x: The x-coordinate of the top-left corner of the region.
    :param y: The y-coordinate of the top-left corner of the region.
    :param w: The w of the region.
    :param h: The h of the region.
    """

    def __init__(self,
                 x: int = 0,
                 y: int = 0,
                 w: int = pg.size().width,
                 h: int = pg.size().height):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.cx = self.x + self.w // 2
        self.cy = self.y + self.h // 2

    def __str__(self):
        return f'Region(x={self.x}, y={self.y}, w={self.w}, h={self.h}, cx={self.cx}, cy={self.cy})'

    def __repr__(self):
        return f'Region(x={self.x}, y={self.y}, w={self.w}, h={self.h}, cx={self.cx}, cy={self.cy})'

    def show(self):
        """
        Show region by Pillow.show() method.
        """
        pg.screenshot(region=self.toTuple()).show()

    def toTuple(self) -> tuple[int, int, int, int]:
        return self.x, self.y, self.w, self.h

    def findText(self, text: str,
                 lang: str = 'eng+rus',
                 contrast: int | float = 0,
                 resize: int = 0,
                 sharpen: bool = True,
                 case_sensitive: bool = False,
                 min_confidence: int = 80,
                 **image_to_data_kwargs
                 ) -> list['Region']:
        """
        Searches for the specified text within the region using OCR and returns regions containing the text.

        :param text: The text to search for.
        :param lang: Language(s) for OCR, separated by a plus sign (e.g., 'eng+rus'). Default is 'eng+rus'.
        :param contrast: Level of contrast enhancement to apply to the image. 0 means no enhancement. Can be a float.
        :param resize: Scaling factor to apply to the image. 0 means no scaling. This is an integer value.
        :param sharpen: Whether to apply a sharpening filter to the image. Default is True.
        :param case_sensitive: Whether the search should be case-sensitive. Default is False.
        :param min_confidence: The minimum confidence level (from 0 to 100) to accept a text match. Default is 0.
        :param image_to_data_kwargs: Additional keyword arguments for pytesseract.image_to_data.
        :return: A list of Region objects containing the matched text. Each region represents the bounding box of the text.
        """
        image = pg.screenshot(region=self.toTuple())

        if resize:
            image = image.resize([int(resize * s) for s in image.size], Image.LANCZOS)
        if contrast:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        if sharpen:
            image = image.filter(ImageFilter.SHARPEN)

        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT,
                                         **image_to_data_kwargs)
        regions = []
        text = text if case_sensitive else text.lower()

        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['conf'][i]) >= min_confidence:
                if case_sensitive:
                    detected_text = data['text'][i]
                else:
                    detected_text = data['text'][i].lower()

                if detected_text == text:
                    (x, y, w, h) = (data['left'][i], data['top'][i], data['w'][i], data['h'][i])
                    regions.append(Region(self.x + x, self.y + y, w, h))

        return regions

    def text(self,
             lang: str = 'eng+rus',
             contrast: int = 0,
             resize: int = 0,
             sharpen: bool = True,
             **image_to_string_kwargs: object) -> str:
        """
        Recognizes and returns the text in the specified area of the screen.

        :param lang: Language(s) for OCR, separated by a plus sign (e.g., 'eng+rus').
        :param contrast: Level of contrast enhancement to apply to the image. 0 means no enhancement.
        :param resize: Scaling factor to apply to the image. 0 means no scaling.
        :param sharpen: Whether to apply a sharpening filter to the image.
        :param image_to_string_kwargs: Additional keyword arguments for pytesseract.image_to_string.
        :return: Recognized text as a string.
        """
        image = pg.screenshot(region=self.toTuple())

        if resize:
            image = image.resize([resize * s for s in image.size], Image.LANCZOS)
        if contrast:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        if sharpen:
            image = image.filter(ImageFilter.SHARPEN)

        return pytesseract.image_to_string(image, lang=lang, **image_to_string_kwargs)

    def click(self, center: bool = True,
              oX: int = 0, oY: int = 0,
              **click_kwargs) -> None:
        """
        Performs a mouse click on the Region.

        :param center: If True, clicks the center of the box; otherwise clicks the top-left corner.
        :param oX: The offset added to the x-coordinate.
        :param oY: The offset added to the y-coordinate.
        :param click_kwargs: Additional keyword arguments for pyautogui.click().
        """
        Point(
            self.cx + oX if center else self.x + oX,
            self.cy + oY if center else self.y + oY,
        ).click(**click_kwargs)

    def moveIn(self, center: bool = True, oX: int = 0, oY: int = 0, **move_kwargs) -> None:
        """
        Moves the mouse cursor in the Region.
        :param center: If True, moves to the center of the box; otherwise moves to the top-left corner.
        :param oX: The offset added to the x-coordinate.
        :param oY: The offset added to the y-coordinate.
        :param move_kwargs: Additional keyword arguments for pyautogui.moveTo().
        """

        move_x = self.cx + oX if center else self.x + oX
        move_y = self.cy + oY if center else self.y + oY
        pg.moveTo(move_x, move_y, **move_kwargs)

    def dragTo(self, to: Point, center: bool = True, oX: int = 0, oY: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current Region and drops to a target x, y.

        :param to: Point where the drag and drop will be performed.
        :param center: If True, starts from the center of the current region; otherwise starts from the top-left corner.
        :param oX: The offset added to the start x-coordinate.
        :param oY: The offset added to the start y-coordinate.
        :param drag_kwargs: Additional keyword arguments for pyautogui.dragTo().
        """
        (Point(self.cx, self.cy)
         if center else
         Point(self.x, self.y)).moveTo(oX, oY)
        pg.dragTo(to.x, to.y, **drag_kwargs)

    def dragRel(self, relX: int, relY: int, center: bool = True, oX: int = 0, oY: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current region to a relative position.

        :param relX: The relative x-coordinate to drag to.
        :param relY: The relative y-coordinate to drag to.
        :param center: If True, starts from the center of the region; otherwise starts from the top-left corner.
        :param oX: The offset added to the start x-coordinate.
        :param oY: The offset added to the start y-coordinate.
        :param drag_kwargs: Additional keyword arguments for pyautogui.dragRel().
        """
        (Point(self.cx, self.cy)
         if center else
         Point(self.x, self.y)).moveTo(oX, oY)
        pg.dragRel(relX, relY, **drag_kwargs)

    @staticmethod
    def removeProximity(regions: list['Region'], proximity_threshold_px: int = 10) -> list['Region']:
        """
        Filters out regions that are within a certain proximity threshold.

        :param regions: List of Region objects to filter.
        :param proximity_threshold_px: Pixel threshold for determining proximity.
        :return: List of filtered Region objects.
        """
        result = []
        for region in regions:
            if not any(abs(region.x - b.x) <= proximity_threshold_px
                       and
                       abs(region.y - b.y) <= proximity_threshold_px
                       for b in result):
                result.append(region)
        return result

    def waitImage(
            self,
            paths: str | tuple[str, ...],
            timeout: int = 10,
            confidence: float = 0.9,
            error_dialog: bool = False,
            check_interval: int = 0.1
    ) -> Union['Region', None]:
        """
        Waits for a specified image or images to appear in the region within a timeout.

        :rtype: object
        :param paths: Path or list of paths to the image(s) to be searched.
        :param timeout: Time in seconds to wait for the image(s).
        :param confidence: The confidence with which to match the image(s).
        :param error_dialog: If True, shows an error dialog if the image is not found.
        :param check_interval: Interval in seconds between checks.
        :return: Point if image is found, None otherwise.
        """
        if isinstance(paths, str):
            paths = [paths]

        end_time = time() + timeout
        while time() < end_time:
            for path in paths:
                try:
                    box = pg.locateOnScreen(path, confidence=confidence, region=self.toTuple())
                    if box is not None:
                        return Region(box.left, box.top, box.w, box.h)
                except pg.ImageNotFoundException:
                    pass
            if timeout == 0:
                return None
            sleep(check_interval)
        # TODO: Исправить отображение paths в этой ошибке
        if error_dialog and not Notify.continueOrStop(f'{paths[0]}'):
            raise pg.ImageNotFoundException

        return None

    def waitImages(
            self,
            paths: str | tuple[str, ...],
            timeout: int = 10,
            confidence: float = 0.9,
            error_dialog: bool = False,
            check_interval: int = 0.1,
            proximity_threshold_px: int = 2,
            min_matches: int = 1
    ) -> list['Region']:
        """
        Waits for multiple images to appear in the region within a specified timeout.

        :param paths: Path or list of paths to the images to be searched.
        :param timeout: Time in seconds to wait for the images.
        :param confidence: The confidence with which to match the images.
        :param error_dialog: If True, shows an error dialog if the images are not found.
        :param check_interval: Interval in seconds between checks.
        :param proximity_threshold_px: Pixel distance to consider images as distinct.
        :param min_matches: Minimum number of matches.
        :return: List of Points or Boxes if images are found, False otherwise.
        """
        if isinstance(paths, str):
            paths = [paths]

        end_time = time() + timeout
        boxes = None
        while time() < end_time:
            for path in paths:
                try:
                    boxes = pg.locateAllOnScreen(path, confidence=confidence, region=self.toTuple())
                    boxes = [Region(b.left, b.top, b.w, b.h) for b in boxes]
                    if boxes:
                        boxes = self.removeProximity(boxes, proximity_threshold_px)
                        if len(boxes) >= min_matches != 0:
                            return boxes
                        continue
                except pg.ImageNotFoundException:
                    pass

            sleep(check_interval)

        if boxes and min_matches == 0:
            return boxes

        # TODO: Исправить отображение paths в этой ошибке
        if error_dialog and not Notify.continueOrStop(f'{paths[0]}'):
            raise pg.ImageNotFoundException
        return []

    def waitColor(self, color, timeout=10, confidence=0.9, error_dialog=False, check_interval=0.1):
        if isinstance(color, str):
            color = hex_to_rgb(color)
        elif isinstance(color, tuple):
            pass
        else:
            raise TypeError(f'{color} color is not a tuple(r,g,b) or string(#rrggbb)')

        start_time = time()
        while True:
            screenshot = ImageGrab.grab(bbox=(self.x, self.y, self.x + self.w, self.y + self.h))
            image = np.array(screenshot)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Check for color in the image
            found, point = self.check_color(image, color, confidence)

            if found:
                # Adjust the point taking into account the region
                corrected_point = (point.x + self.x, point.y + self.y)
                return Point(*corrected_point)

            if time() - start_time > timeout:
                if error_dialog:
                    print("Color not found")
                return None

            sleep(check_interval)

    @staticmethod
    def check_color(image, color, confidence):
        # Преобразование цвета в формат BGR
        bgr_color = color[::-1]

        # Рассчитываем границы для заданного диапазона цветов с учетом confidence
        lower_bound = np.array([max(0, c - (255 - c) * (1 - confidence)) for c in bgr_color])
        upper_bound = np.array([min(255, c + (255 - c) * (1 - confidence)) for c in bgr_color])
        mask = cv2.inRange(image, lower_bound, upper_bound)

        # Находим координаты точки
        points = np.where(mask == 255)
        if len(points[0]) > 0:
            y, x = points[0][0], points[1][0]
            return True, Point(x, y)

        return False, None
        # def waitColor(

    def waitColors(
            self,
            color: str | tuple[str, ...],
            timeout: int = 10000,
            confidence: float = 0.9,
            error_dialog: bool = False,
            check_interval: int = 100,
            proximity_threshold_px: int = 2,
            min_matches: int = 0
    ) -> list[Point] | None:
        """
        Waits for multiple colors to appear in the region within a specified timeout.

        :param color: Color or list of colors to be searched.
        :param timeout: Time in milliseconds to wait for the colors.
        :param confidence: The confidence with which to match the colors.
        :param error_dialog: If True, shows an error dialog if the colors are not found.
        :param check_interval: Interval in milliseconds between checks.
        :param proximity_threshold_px: Pixel distance to consider colors as distinct.
        :param min_matches: Minimum number of matches. If 0 then all matches will be returned.
        :return: List of Points where the colors are found, or None if not found.
        """
        if isinstance(color, str):
            if color.startswith('#'):
                color = hex_to_rgb(color)
            else:
                color = [color]
        elif isinstance(color, tuple):
            color = [hex_to_rgb(c) if isinstance(c, str) and c.startswith('#') else c for c in color]

        end_time = time() + (timeout / 1000)
        matches = []
        region = self.toTuple()
        while time() < end_time:
            for x in range(region[0], region[2]):
                for y in range(region[1], region[3]):
                    for c in color:
                        if pixelMatchesColor(x, y, c, tolerance=int(255 * (1 - confidence))):
                            matches.append(Point(x, y))
                            if len(matches) >= min_matches != 0:
                                return Point.removeProximity(matches, proximity_threshold_px)
                            break
            sleep(check_interval / 1000)

        if matches and min_matches == 0:
            return Point.removeProximity(matches, proximity_threshold_px)
        if error_dialog:
            Notify.continueOrStop(f'Colors {color[0]} not found')
        return None

