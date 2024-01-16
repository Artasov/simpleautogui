from simpleautogui.base.classes.base import Region, Point


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
