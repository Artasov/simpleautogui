from time import time, sleep

from pyautogui import size
from pyscreeze import pixelMatchesColor, ImageNotFoundException

from simpleautogui.base.classes.base import Point
from simpleautogui.base.classes.notify import Notify
from simpleautogui.screen.utils.proximity import remove_proximity_points


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

    if error_dialog and not Notify.confirm(f'{color[0]}'):
        raise ImageNotFoundException
    return False


def waitColors(
        colors: tuple[str, list[str]],
        timeout: int = 10000,
        confidence: float = 0.9,
        error_dialog: bool = False,
        region: tuple[int, int, int, int] = (0, 0, size().width, size().height),
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
    if error_dialog and not Notify.confirm(f'{colors[0]}'):
        raise ImageNotFoundException
    return None
