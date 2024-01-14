import pyautogui as pg
import pytesseract
from PIL import ImageEnhance, ImageFilter
from PIL import Image


class Point:
    def __init__(self, x: int, y: int):
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

    def dragDropTo(self, endX, endY, oX: int = 0, oY: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current Point with offset and drops to a target x,y.

        :param endX: Finish x-coordinate
        :param endY: Finish y-coordinate
        :param oX: The offset added to the start x-coordinate.
        :param oY: The offset added to the start y-coordinate.
        :param drag_kwargs: Additional keyword arguments for pyautogui.dragTo().
        """
        pg.dragTo(self.x + oX, self.y + oY, endX, endY, **drag_kwargs)

    def dragDropRel(self, relX: int, relY: int, oX: int = 0, oY: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current Point with offset to a relative position.

        :param relX: The relative x-coordinate to drag to.
        :param relY: The relative y-coordinate to drag to.
        :param oX: The offset added to the start x-coordinate.
        :param oY: The offset added to the start y-coordinate.
        :param drag_kwargs: Additional keyword arguments for pyautogui.dragRel().
        """
        pg.dragRel(self.x + oX, self.y + oY, relX, relY, **drag_kwargs)


class Region:
    """
    Represents a rectangular area on the screen, providing methods to interact with it.

    :param x: The x-coordinate of the top-left corner of the region.
    :param y: The y-coordinate of the top-left corner of the region.
    :param width: The width of the region.
    :param height: The height of the region.
    """

    def __init__(self, x: int, y: int, width: int, height: int):
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

    def findText(self, text: str, lang: str = 'eng+rus', contrast: int = 0,
                 resize: int = 0, sharpen: bool = True, case_sensitive: bool = False,
                 **image_to_string_kwargs):
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
            image = image.resize([resize * s for s in image.size], Image.LANCZOS)
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

            if text.startswith(current_text + char):
                if not current_text:  # first character of the match
                    current_region = [int(b[1]), int(b[2]), int(b[3]), int(b[4])]
                else:  # expand the region to include current char
                    current_region[2] = int(b[3])
                    current_region[3] = int(b[4])

                current_text += char

                if current_text == text:  # full match
                    x, y, w, h = current_region
                    print(f'{current_region=}')
                    regions.append(Region(self.x + x, self.y + y, w, h))
                    current_text = ""  # reset for next possible match
            else:
                current_text = ""  # reset current text as it's not a match

        return regions

    def text(self, lang: str = 'eng+rus', contrast: int = 0, resize: int = 0,
             sharpen: bool = True, **image_to_string_kwargs) -> str:
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

    def dragDropTo(self, endX, endY, center: bool = True, oX: int = 0, oY: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current box and drops to a target box.

        :param endX: Finish x-coordinate
        :param endY: Finish y-coordinate
        :param center: If True, starts from the center of the current box.
        :param oX: The offset added to the start x-coordinate.
        :param oY: The offset added to the start y-coordinate.
        :param drag_kwargs: Additional keyword arguments for pyautogui.dragTo().
        """
        start_x = self.cx + oX if center else self.x + oX
        start_y = self.cy + oY if center else self.y + oY
        pg.dragTo(start_x, start_y, endX, endY, **drag_kwargs)

    def dragDropRel(self, relX: int, relY: int, center: bool = True, oX: int = 0, oY: int = 0, **drag_kwargs) -> None:
        """
        Drags from the current box to a relative position.

        :param relX: The relative x-coordinate to drag to.
        :param relY: The relative y-coordinate to drag to.
        :param center: If True, starts from the center of the box.
        :param oX: The offset added to the start x-coordinate.
        :param oY: The offset added to the start y-coordinate.
        :param drag_kwargs: Additional keyword arguments for pyautogui.dragRel().
        """
        start_x = self.cx + oX if center else self.x + oX
        start_y = self.cy + oY if center else self.y + oY
        pg.dragRel(start_x, start_y, relX, relY, **drag_kwargs)
