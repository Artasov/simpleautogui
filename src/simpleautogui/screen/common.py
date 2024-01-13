from typing import List

import pyautogui as pg
from pyautogui import Point
from pyrect import Box


def wait_while_img_not_found(pathes, check_count=100, accur=0.8, err_skipping=False,
                             region=(0, 0, pg.size().width, pg.size().height), sleep_sec=0, center=True):
    from time import sleep
    check_now = 0
    if isinstance(pathes, str):
        pathes = [pathes]
    while check_now < check_count:
        if check_now + 1 < check_count:
            sleep(sleep_sec)
        else:
            if not err_skipping:
                if not search_notify_error(f'{pathes[0]}'):
                    return False
                check_now = 0
        for onePath in pathes:
            if center:
                point = pg.locateCenterOnScreen(onePath, confidence=accur, region=region)
            else:
                point = pg.locateOnScreen(onePath, confidence=accur, region=region)
            if point is not None:
                return point
        check_now += 1
    return False


def click_to_image(pathes, check_count=100, accur=0.8, err_skipping=False, oX=0, oY=0,
                   region=(0, 0, pg.size().width, pg.size().height), sleep_sec=0, center=True):
    position: Point = wait_while_img_not_found(pathes, check_count, accur, err_skipping,
                                               region, sleep_sec, center)
    if position:
        pg.click(position.x + oX, position.y + oY)


def wait_while_img_not_found_all(pathes, check_count=100, accur=0.8, err_skipping=False,
                                 region=(0, 0, pg.size().width, pg.size().height), sleep_sec=0,
                                 pixel_accur_near_points=10, return_centers_points=True):
    from time import sleep
    if isinstance(pathes, str):
        pathes = [pathes]
    check_now = 0
    while check_now < check_count:
        if check_now + 1 < check_count:
            sleep(sleep_sec)
        else:
            if not err_skipping:
                if not search_notify_error(f'{pathes}'):
                    return False
                check_now = 0
        for path in pathes:
            result = pg.locateAllOnScreen(path, confidence=accur, region=region)
            boxes = list(result)
            if len(boxes) > 0:
                if return_centers_points:
                    return get_center_points_in_boxes(
                        remove_near_boxes(boxes, pixel_accur_near_points=pixel_accur_near_points)
                    )
                else:
                    return remove_near_boxes(boxes, pixel_accur_near_points=pixel_accur_near_points)
        check_now += 1
    return False


def remove_near_boxes(boxes: List[Box], pixel_accur_near_points: int = 10) -> List[Box]:
    result = []
    for box in boxes:
        box: Box
        if not any(abs(box.left - b.left) <= pixel_accur_near_points and abs(box.top - b.top) <= pixel_accur_near_points
                   for b in result):
            result.append(box)
    return result


def get_center_points_in_boxes(boxes: List[Box]) -> List[Point]:
    center_points = []
    for box in boxes:
        center_points.append(Point(x=box.left + int(box.width / 2), y=box.top + int(box.height / 2)))
    return center_points


def search_notify_error(error_msg):
    msg = f'SEARCH ERROR {error_msg}'
    result = pg.confirm(msg, 'CONFIRMATION', ('Continue search', 'Stop'))
    if result == 'Continue search':
        return True
    else:
        return False
