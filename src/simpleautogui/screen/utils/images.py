from time import sleep, time
from pyautogui import (
    locateOnScreen,
    size,
    locateAllOnScreen, ImageNotFoundException
)

from simpleautogui.base.classes.base import Region
from simpleautogui.base.classes.notify import Notify
from simpleautogui.screen.utils.proximity import remove_proximity_boxes


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

    if error_dialog and not Notify.confirm(f'{paths[0]}'):
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
) -> list[Region]:
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

    if error_dialog and not Notify.confirm(f'{paths[0]}'):
        raise ImageNotFoundException
    return []
