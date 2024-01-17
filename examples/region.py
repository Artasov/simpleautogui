from simpleautogui import Region

# Define a region starting at x=100, y=200 with width=300 and height=400.
r = Region(100, 200, 300, 400)

# Click to the center at this region.
# r.click()
# r.click(center=False) u can.

# Move the mouse to region center.
# r.moveTo()
# center=False u can.

# Show this region (save screenshot like .png in local/temp and open it).
# r.show()

# Recognizes and returns the text in the specified area of the screen.
# We find the Tesseract-OCR path in the path variable to tesseract.exe.
# Example with default arguments:
# r.text(
#     lang='eng+rus',  # Language(s) for OCR, separated by a plus sign (e.g., 'eng+rus').
#     contrast=0,  # Level of contrast enhancement to apply to the image. 0 means no enhancement.
#     resize=0,  # Scaling factor to apply to the image. 0 means no scaling.
#     sharpen=True,  # Whether to apply a sharpening filter to the image.
# )
# Use something like this:
# if 'some text' in r.text():
#     pass

# Search for text throughout the entire screen.
# Let's try to find an application called Adobe on the taskbar.
# Return the list of Region objects containing the text.
from pyautogui import size


taskbar = Region()
# taskbar.show()
# print(f'Taskbar text: {taskbar.text(resize=3)}')

# result: list[Region] = taskbar.findText('Window')
# if result:
#     print(result[0])
#     result[0].moveTo()
# else:
#     print('Not found... Let\'s try to increase the size and increase the contrast')

# More arguments
result: list[Region] = taskbar.findText(
    text='Window',
    lang='eng+rus',
    contrast=0,
    resize=0,
    sharpen=True,
    case_sensitive=False,
    min_confidence=80
)
if result:
    print(result[0])
    result[0].moveTo(center=True)
else:
    print('Not found... Try another image.')
