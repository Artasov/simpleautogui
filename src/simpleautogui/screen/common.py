from time import sleep, time
from typing import List, Union, Tuple

import pyrect
from pyautogui import (
    Point,
    locateOnScreen,
    size,
    confirm,
    locateAllOnScreen, ImageNotFoundException
)

from simpleautogui.screen.classes.common import Box


def wait_for_image(
        paths: str | list[str],
        timeout: int = 10000,
        accuracy: float = 0.8,
        error_dialog: bool = False,
        region: tuple[int, int, int, int] = (0, 0, size().width, size().height),
        check_interval: int = 100
) -> Box | None:
    """
    Waits for a specified image or images to appear on the screen within a timeout.

    :param paths: Path or list of paths to the image(s) to be searched.
    :param timeout: Time in milliseconds to wait for the image(s).
    :param accuracy: The accuracy with which to match the image(s).
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
                box = locateOnScreen(path, confidence=accuracy, region=region)
                if box is not None:
                    return Box(box.left, box.top, box.width, box.height)
            except ImageNotFoundException:
                pass
        sleep(check_interval / 1000)

        if time() >= end_time and not error_dialog:
            if not notify_error(f'{paths[0]}'):
                return None

    return None


def wait_for_images(
        paths: str | List[str],
        timeout: int = 10000,
        accuracy: float = 0.8,
        error_dialog: bool = False,
        region: Tuple[int, int, int, int] = (0, 0, size().width, size().height),
        check_interval: int = 100,
        proximity_threshold_px: int = 4,
) -> list[Point] | list[Box] | None:
    """
    Waits for multiple images to appear on the screen within a specified timeout.

    :param paths: Path or list of paths to the images to be searched.
    :param timeout: Time in milliseconds to wait for the images.
    :param accuracy: The accuracy with which to match the images.
    :param error_dialog: If True, shows an error dialog if the images are not found.
    :param region: The region of the screen to search in.
    :param check_interval: Interval in milliseconds between checks.
    :param proximity_threshold_px: Pixel distance to consider images as distinct.
    :return: List of Points or Boxes if images are found, False otherwise.
    """
    if isinstance(paths, str):
        paths = [paths]

    end_time = time() + (timeout / 1000)
    while time() < end_time:
        for path in paths:
            try:
                boxes = locateAllOnScreen(path, confidence=accuracy, region=region)
                boxes = [Box(b.left, b.top, b.width, b.height) for b in boxes]
                if boxes:
                    boxes = remove_proximity_boxes(boxes, proximity_threshold_px)
                    return boxes
            except ImageNotFoundException:
                pass

        sleep(check_interval / 1000)
        if time() >= end_time and not error_dialog:
            if not notify_error(f'{paths[0]}'):
                return None

    return None


def remove_proximity_boxes(boxes: list[Box], proximity_threshold_px: int = 10) -> list[Box]:
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


def notify_error(msg: str) -> bool:
    """
    Displays an error dialog and asks the user whether to continue after this error.

    :param msg: The error message to display.
    :return: True if the user chooses to continue the search, False otherwise.
    """
    result = confirm(msg, 'Confirmation', ('Continue ', 'Stop'))
    return result == 'Continue'
