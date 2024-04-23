from pyautogui import size

from simpleautogui import Region

# Waits for the image to appear and clicks on its center.
Region().waitImage('image.png').click()

# Waits for one of several images to appear and clicks...
Region().waitImage(('image.png', 'image2.png')).click()

result: Region | None = Region().waitImage(
    paths='image.png',  # Path or tuple of paths to the images to be searched.
    timeout=10000,  # Time in milliseconds to wait for the images.
    confidence=0.9,  # The confidence with which to match the images.
    error_dialog=False,  # If True, shows an error dialog if the images are not found.
    # Displays an error dialog and asks the user whether to continue exec code or stop.
    check_interval=100,  # Interval in milliseconds between checks.
)
result.click()

images = Region().waitImages('image.png')
for img in images:
    img.click()

# with args
images: Region | [] = Region().waitImages(
    paths='image.png',  # Path or tuple of paths to the images to be searched.
    timeout=10000,  # Time in milliseconds to wait for the images.
    confidence=0.9,  # The confidence with which to match the images.
    error_dialog=False,  # If True, shows an error dialog if the images are not found.
    check_interval=100,  # Interval in milliseconds between checks.
    proximity_threshold_px=2,  # Pixel distance to consider images as distinct.
    min_matches=1  # Minimum number of matches.
)
