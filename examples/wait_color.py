from pyautogui import size
from simpleautogui import Point
from simpleautogui.screen import waitColor, waitColors

point: Point = waitColor('red')
if point:
    print(f"Found red color at {point.x}, {point.y}")
else:
    print("Red color not found")

point: Point = waitColor(
    color=('#00ff00', 'rgb(255, 0, 0)'),
    timeout=10000,
    confidence=0.9,
    error_dialog=False,
    region=(0, 0, size().w, size().h),
    check_interval=100
)
if point:
    point.moveIn()
else:
    print("Green color not found")

points: list[Point] = waitColors(
    color=('rgb(255, 0, 0)', '#00ff00', 'blue'),
    timeout=10000,
    confidence=0.9,
    error_dialog=False,
    region=(0, 0, size().w, size().h),
    check_interval=100,
    proximity_threshold_px=2,
    min_matches=0  # if 0 return all founded else count first founded
)
if points:
    for point in points:
        point.moveIn()
else:
    print("Specified colors not found")
