from simpleautogui.screen.classes.base import Point, Region


def wait_color(color, region: Region | tuple[int, int, int, int] | None = None, **kwargs):
    target_region = region if isinstance(region, Region) else Region(*(region or ()))
    return target_region.wait_color(color, **kwargs)


def wait_colors(color, region: Region | tuple[int, int, int, int] | None = None, **kwargs):
    target_region = region if isinstance(region, Region) else Region(*(region or ()))
    return target_region.wait_colors(color, **kwargs)
