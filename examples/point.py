from time import sleep

from simpleautogui import Point

# print(Point().get_deviation())
# sleep(1)
# print(Point().get_distance())

# Create a points with x and y coordinates
p = Point(100, 100)
p2 = Point(500, 500)
# Click at first point
p.click()
# Move the mouse to first point
p.moveTo(duration=5)
# Drag and drop 'p' to 'p2'.
p.dragDropTo(p2.x, p2.y, duration=5)
# Drag and drop by offset
p.dragDropRel(400, 400, duration=5)

p.click(
    oX=0,  # Y offset
    oY=0,  # X offset
    clicks=2,  # double click
    interval=0.0,  # interval between clicks in seconds
    button='right',  # 'left', 'middle'
    logScreenshot=True,  # screenshot logging
)

p.moveTo(
    oX=0,
    oY=0,
    # **move_kwargs
    duration=0.0,
    logScreenshot=False,
)
# dragTo, dragRel same
