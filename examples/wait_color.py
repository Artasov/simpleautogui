from pyautogui import size
from simpleautogui import Point
from simpleautogui import Region

point: Point = Region().wait_color('red')
if point:
    print(f"Found red color at {point.x}, {point.y}")
else:
    print("Red color not found")

point: Point = Region(0, 0, size().w, size().h).wait_color(
    color='#00ff00',
    timeout=10,
    confidence=0.9,
    error_dialog=False,
    check_interval=0.1
)
if point:
    point.move_in()
else:
    print("Green color not found")

points: list[Point] = Region(0, 0, size().w, size().h).wait_colors(
    color=('rgb(255, 0, 0)', '#00ff00', 'blue'),
    timeout=10,
    confidence=0.9,
    error_dialog=False,
    check_interval=0.1,
    proximity_threshold_px=2,
    min_matches=0  # if 0 return all found matches from the first matching screenshot
)
if points:
    for point in points:
        point.move_in()
else:
    print("Specified colors not found")
