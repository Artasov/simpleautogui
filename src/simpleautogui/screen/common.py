from time import sleep, time
from typing import List, Union, Tuple
from pyscreeze import pixelMatchesColor

from simpleautogui.screen.classes.common import Region, Point
from pyautogui import (
    locateOnScreen,
    size,
    confirm,
    locateAllOnScreen, ImageNotFoundException
)


def waitColor(
        color: str | list[str],
        timeout: int = 10000,
        confidence: float = 0.9,
        error_dialog: bool = False,
        region: tuple[int, int, int, int] = (0, 0, size().width, size().height),
        check_interval: int = 100
) -> bool:
    """
    Waits for a specified color or colors to appear on the screen within a timeout.

    :param color: Color or list of colors to be searched.
    :param timeout: Time in milliseconds to wait for the color(s).
    :param confidence: The confidence with which to match the color(s).
    :param error_dialog: If True, shows an error dialog if the color is not found.
    :param region: The region of the screen to search in.
    :param check_interval: Interval in milliseconds between checks.
    :return: True if color is found, False otherwise.
    """
    if isinstance(color, str):
        color = [color]

    end_time = time() + (timeout / 1000)
    while time() < end_time:
        for x in range(region[0], region[2]):
            for y in range(region[1], region[3]):
                if any(pixelMatchesColor(x, y, c, tolerance=255 * (1 - confidence)) for c in color):
                    return True
        sleep(check_interval / 1000)

    if error_dialog and not notify_error(f'{color[0]}'):
        raise ImageNotFoundException
    return False


def waitColors(
        colors: Union[str, List[str]],
        timeout: int = 10000,
        confidence: float = 0.9,
        error_dialog: bool = False,
        region: Tuple[int, int, int, int] = (0, 0, size().width, size().height),
        check_interval: int = 100,
        proximity_threshold_px: int = 2,
        min_matches: int = 0
) -> list[Point] | None:
    """
    Waits for multiple colors to appear on the screen within a specified timeout.

    :param colors: Color or list of colors to be searched.
    :param timeout: Time in milliseconds to wait for the colors.
    :param confidence: The confidence with which to match the colors.
    :param error_dialog: If True, shows an error dialog if the colors are not found.
    :param region: The region of the screen to search in.
    :param check_interval: Interval in milliseconds between checks.
    :param proximity_threshold_px: Pixel distance to consider colors as distinct.
    :param min_matches: Minimum number of matches. If 0 then all matches will be returned.
    :return: True if colors are found, False otherwise.
    """
    if isinstance(colors, str):
        colors = [colors]

    end_time = time() + (timeout / 1000)
    matches = []
    while time() < end_time:
        for x in range(region[0], region[2]):
            for y in range(region[1], region[3]):
                for c in colors:
                    if pixelMatchesColor(x, y, c, tolerance=255 * (1 - confidence)):
                        matches.append(Point(x, y))
                        if len(matches) >= min_matches != 0:
                            return remove_proximity_points(matches, proximity_threshold_px)
                        break
        sleep(check_interval / 1000)

    if matches and min_matches == 0:
        return remove_proximity_points(matches, proximity_threshold_px)
    if error_dialog and not notify_error(f'{colors[0]}'):
        raise ImageNotFoundException
    return None


def waitImage(
        paths: str | list[str],
        timeout: int = 10000,
        confidence: float = 0.9,
        error_dialog: bool = False,
        region: tuple[int, int, int, int] = (0, 0, size().width, size().height),
        check_interval: int = 100
) -> Region | None:
    """
    Waits for a specified image or images to appear on the screen within a timeout.

    :param paths: Path or list of paths to the image(s) to be searched.
    :param timeout: Time in milliseconds to wait for the image(s).
    :param confidence: The confidence with which to match the image(s).
    :param error_dialog: If True, shows an error dialog if the image is not found.
    :param region: The region of the screen to search in.
    :param check_interval: Interval in milliseconds between checks.
    :return: Point if image is found, None otherwise.
    """
    if isinstance(paths, str):
        paths = [paths]

    end_time = time() + (timeout / 1000)
    while time() < end_time:
        for path in paths:
            try:
                box = locateOnScreen(path, confidence=confidence, region=region)
                if box is not None:
                    return Region(box.left, box.top, box.width, box.height)
            except ImageNotFoundException:
                pass
        sleep(check_interval / 1000)

    if error_dialog and not notify_error(f'{paths[0]}'):
        raise ImageNotFoundException

    return None


def waitImages(
        paths: str | list[str],
        timeout: int = 10000,
        confidence: float = 0.9,
        error_dialog: bool = False,
        region: tuple[int, int, int, int] = (0, 0, size().width, size().height),
        check_interval: int = 100,
        proximity_threshold_px: int = 2,
        min_matches: int = 1
) -> list[Region] | None:
    """
    Waits for multiple images to appear on the screen within a specified timeout.

    :param paths: Path or list of paths to the images to be searched.
    :param timeout: Time in milliseconds to wait for the images.
    :param confidence: The confidence with which to match the images.
    :param error_dialog: If True, shows an error dialog if the images are not found.
    :param region: The region of the screen to search in.
    :param check_interval: Interval in milliseconds between checks.
    :param proximity_threshold_px: Pixel distance to consider images as distinct.
    :param min_matches: Minimum number of matches.
    :return: List of Points or Boxes if images are found, False otherwise.
    """
    if isinstance(paths, str):
        paths = [paths]

    end_time = time() + (timeout / 1000)
    boxes = None
    while time() < end_time:
        for path in paths:
            try:
                boxes = locateAllOnScreen(path, confidence=confidence, region=region)
                boxes = [Region(b.left, b.top, b.width, b.height) for b in boxes]
                if boxes:
                    boxes = remove_proximity_boxes(boxes, proximity_threshold_px)
                    if len(boxes) >= min_matches != 0:
                        return boxes
                    continue
            except ImageNotFoundException:
                pass

        sleep(check_interval / 1000)

    if boxes and min_matches == 0:
        return boxes

    if error_dialog and not notify_error(f'{paths[0]}'):
        raise ImageNotFoundException
    return None


def remove_proximity_boxes(boxes: list[Region], proximity_threshold_px: int = 10) -> list[Region]:
    """
    Filters out boxes that are within a certain proximity threshold.

    :param boxes: List of Box objects to filter.
    :param proximity_threshold_px: Pixel threshold for determining proximity.
    :return: List of filtered Box objects.
    """
    result = []
    for box in boxes:
        if not any(abs(box.x - b.x) <= proximity_threshold_px and abs(box.y - b.y) <= proximity_threshold_px
                   for b in result):
            result.append(box)
    return result


def remove_proximity_points(points: list[Point], proximity_threshold_px: int) -> list[Point]:
    """
    Filters out points that are within a certain proximity threshold.

    :param points: List of Point objects to filter.
    :param proximity_threshold_px: Pixel threshold for determining proximity.
    :return: List of filtered Point objects.
    """
    result = []
    for point in points:
        if not any(abs(point.x - p.x) <= proximity_threshold_px and abs(point.y - p.y) <= proximity_threshold_px
                   for p in result):
            result.append(point)
    return result


def notify_error(msg: str) -> bool:
    """
    Displays an error dialog and asks the user whether to continue after this error.

    :param msg: The error message to display.
    :return: True if the user chooses to continue the search, False otherwise.
    """
    result = confirm(msg, 'Confirmation', ('Continue ', 'Stop'))
    return result == 'Continue'
