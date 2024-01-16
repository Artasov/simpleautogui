import math
from time import time, sleep
from typing import Union

import keyboard
import pyautogui as pg
import pytesseract
from PIL import ImageEnhance, ImageFilter
from PIL import Image
import mouse


class Point:
    def __init__(self, x: int = 0, y: int = 0):
        self.clicked_position = None
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
        :param move_kwargs: Additional keyword arguments for pyautogui.moveTo().
        """

        pg.moveTo(self.x + oX, self.y + oY, **move_kwargs)

    def dragDropTo(self, endX: int, endY: int, oX: int = 0, oY: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current Point with offset and drops to a target x,y.
        """
        # Move to the starting point with offset
        pg.moveTo(self.x + oX, self.y + oY)

        # Drag to the end point
        pg.dragTo(endX, endY, **drag_kwargs)

    def dragDropRel(self, relX: int, relY: int, oX: int = 0, oY: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current Point with offset to a relative position.
        """
        # Move to the starting point with offset
        pg.moveTo(self.x + oX, self.y + oY)

        # Drag to the relative position
        pg.dragRel(relX, relY, **drag_kwargs)

    @staticmethod
    def input(button='right', timeout=10) -> Union['Point', None]:
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

            if button in ['left', 'right', 'middle'] and mouse.is_pressed(button):
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

        :param sleep_after_first: Sleep seconds after first click.
        :param with_sign: If True, returns the distance considering the sign. If False, returns the absolute distance.
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
    def get_deviation(with_sign: bool = True, sleep_after_first: float | int = 0.2) -> tuple[int, int]:
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


class Region:
    """
    Represents a rectangular area on the screen, providing methods to interact with it.

    :param x: The x-coordinate of the top-left corner of the region.
    :param y: The y-coordinate of the top-left corner of the region.
    :param width: The width of the region.
    :param height: The height of the region.
    """

    def __init__(self,
                 x: int = 0,
                 y: int = 0,
                 width: int = pg.size().width,
                 height: int = pg.size().height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.cx = self.x + self.width // 2
        self.cy = self.y + self.height // 2

    def __str__(self):
        return f'Region(x={self.x}, y={self.y}, w={self.width}, h={self.height}, cx={self.cx}, cy={self.cy})'

    def __repr__(self):
        return f'Region(x={self.x}, y={self.y}, w={self.width}, h={self.height}, cx={self.cx}, cy={self.cy})'

    def show(self):
        """
        Show region by Pillow.show() method.
        """
        image = pg.screenshot(region=(self.x, self.y, self.width, self.height))
        image.show()

    def findText(self, text: str, lang: str = 'eng+rus', contrast: int | float = 0,
                 resize: int = 0, sharpen: bool = True, case_sensitive: bool = False,
                 **image_to_string_kwargs) -> list['Region']:
        """
        Searches for the specified text within the region and returns regions containing the text.

        :param text: The text to search for.
        :param lang: Language(s) for OCR, separated by a plus sign (e.g., 'eng+rus').
        :param contrast: Level of contrast enhancement to apply to the image. 0 means no enhancement.
        :param resize: Scaling factor to apply to the image. 0 means no scaling.
        :param sharpen: Whether to apply a sharpening filter to the image.
        :param case_sensitive: Whether the search should be case-sensitive.
        :param image_to_string_kwargs: Additional keyword arguments for pytesseract.image_to_boxes.
        :return: List of Region objects containing the text.
        """
        image = pg.screenshot(region=(self.x, self.y, self.width, self.height))

        if resize:
            image = image.resize([int(resize * s) for s in image.size], Image.LANCZOS)
        if contrast:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        if sharpen:
            image = image.filter(ImageFilter.SHARPEN)

        boxes = pytesseract.image_to_boxes(image, lang=lang, **image_to_string_kwargs)
        regions = []
        text = text if case_sensitive else text.lower()
        current_text = ""
        current_region = [0, 0, 0, 0]

        for box in boxes.splitlines():
            b = box.split(' ')
            char = b[0]
            char = char if case_sensitive else char.lower()

            # Adjusted the coordinates to account for the region's position
            x1, y1, x2, y2 = map(int, b[1:5])
            y1 = image.height - y1
            y2 = image.height - y2

            if text.startswith(current_text + char):
                if not current_text:  # first character of the match
                    current_region = [x1, y2, x2, y1]
                else:  # expand the region to include current char
                    current_region[2] = x2
                    current_region[3] = y1

                current_text += char

                if current_text == text:  # full match
                    x, y, w, h = current_region
                    regions.append(Region(self.x + x, self.y + y, w - x, h - y))
                    current_text = ""  # reset for next possible match
            else:
                current_text = ""  # reset current text as it's not a match

        return regions

    def text(self, lang: str = 'eng+rus', contrast: int = 0, resize: int = 0,
             sharpen: bool = True, **image_to_string_kwargs: object) -> str:
        """
        Recognizes and returns the text in the specified area of the screen.

        :param lang: Language(s) for OCR, separated by a plus sign (e.g., 'eng+rus').
        :param contrast: Level of contrast enhancement to apply to the image. 0 means no enhancement.
        :param resize: Scaling factor to apply to the image. 0 means no scaling.
        :param sharpen: Whether to apply a sharpening filter to the image.
        :param image_to_string_kwargs: Additional keyword arguments for pytesseract.image_to_string.
        :return: Recognized text as a string.
        """
        image = pg.screenshot(region=(self.x, self.y, self.width, self.height))

        if resize:
            image = image.resize([resize * s for s in image.size], Image.LANCZOS)
        if contrast:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        if sharpen:
            image = image.filter(ImageFilter.SHARPEN)

        return pytesseract.image_to_string(image, lang=lang, **image_to_string_kwargs)

    def click(self, center: bool = True, oX: int = 0, oY: int = 0, **click_kwargs) -> None:
        """
        Performs a mouse click on the box.

        :param center: If True, clicks the center of the box; otherwise clicks the top-left corner.
        :param oX: The offset added to the x-coordinate.
        :param oY: The offset added to the y-coordinate.
        :param click_kwargs: Additional keyword arguments for pyautogui.click().
        """
        click_x = self.cx + oX if center else self.x + oX
        click_y = self.cy + oY if center else self.y + oY
        pg.click(click_x, click_y, **click_kwargs)

    def moveTo(self, center: bool = True, oX: int = 0, oY: int = 0, **move_kwargs) -> None:
        """
        Moves the mouse cursor to the box.
        :param center: If True, moves to the center of the box; otherwise moves to the top-left corner.
        :param oX: The offset added to the x-coordinate.
        :param oY: The offset added to the y-coordinate.
        :param move_kwargs: Additional keyword arguments for pyautogui.moveTo().
        """

        move_x = self.cx + oX if center else self.x + oX
        move_y = self.cy + oY if center else self.y + oY
        pg.moveTo(move_x, move_y, **move_kwargs)

    def dragDropTo(self, endX: int, endY: int, center: bool = True, oX: int = 0, oY: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current box and drops to a target x, y.

        :param endX: Finish x-coordinate.
        :param endY: Finish y-coordinate.
        :param center: If True, starts from the center of the current box; otherwise starts from the top-left corner.
        :param oX: The offset added to the start x-coordinate.
        :param oY: The offset added to the start y-coordinate.
        :param drag_kwargs: Additional keyword arguments for pyautogui.dragTo().
        """
        start_x = self.cx + oX if center else self.x + oX
        start_y = self.cy + oY if center else self.y + oY
        pg.moveTo(start_x, start_y)
        pg.dragTo(endX, endY, **drag_kwargs)

    def dragDropRel(self, relX: int, relY: int, center: bool = True, oX: int = 0, oY: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current box to a relative position.

        :param relX: The relative x-coordinate to drag to.
        :param relY: The relative y-coordinate to drag to.
        :param center: If True, starts from the center of the box; otherwise starts from the top-left corner.
        :param oX: The offset added to the start x-coordinate.
        :param oY: The offset added to the start y-coordinate.
        :param drag_kwargs: Additional keyword arguments for pyautogui.dragRel().
        """
        start_x = self.cx + oX if center else self.x + oX
        start_y = self.cy + oY if center else self.y + oY
        pg.moveTo(start_x, start_y)
        pg.dragRel(relX, relY, **drag_kwargs)
