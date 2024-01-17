# Introduction to `simpleautogui` <br>[Read the docs]()

`simpleautogui` is a Python library designed to automate
interaction with graphical user interfaces on Windows operating
systems through scripting. Leveraging the power of several
underlying libraries, it provides a set of tools to simulate
human interaction with the computer in a straightforward and
efficient manner.

## Modules and Functionality
 
The library is organized into several modules, each providing
distinct functionalities:

* `Base`: Defines the fundamental classes like `Point` and `Region`
  for screen regions and coordinates.
* `Screen`: Contains utilities for image and color recognition,
  waiting for elements to appear.
* `Win`: Provides functions to manipulate window geometry, search
  for windows by title, and arrange windows in a grid
  pattern.

The function `waitImage` waits for a specific image to
appear on the screen, while waitImages handles multiple images.
`waitColor` and `waitColors` perform similar operations for color
detection. The Region class allows for capturing
screenshots, finding text, and clicking within specific screen regions.
The win module's `set_window_geometry` enables
precise control over window size and position, essential for creating a
consistent automated environment.

This library is under the MIT License, ensuring open-source 
accessibility and the freedom to integrate it into various
projects. The combination of its robust feature set and the ease 
of use makes simpleautogui a valuable tool for
automating GUI interactions on Windows.

## Dependencies

`simpleautogui` relies on the following dependencies:

* Python 3.11 or higher
* PyAutoGUI
* OpenCV-Python
* PyWin32
* PyTesseract
* Mouse
* Webcolors
* Keyboard

## Quick Start

To get started with **simpleautogui**, install the package using pip:

```sh
pip install simpleautogui
```

  * ## Classes

    **simpleautogui** provides two main classes: **Point** and **Region**,
    which facilitate screen interaction.

    * ### Point
      The **Point** class represents a specific location on the screen.
      It provides methods to perform actions like clicking or moving
      the mouse to its coordinates.

      ```python
      from simpleautogui import Point
      
      # Create a points with x and y coordinates
      p = Point(100, 100)
      p2 = Point(500, 500)
      # Click at first point
      p.click()
      # Move the mouse to first point
      p.moveTo()
      # Drag and drop 'p' to 'p2'.
      p.dragDropTo(p2.x, p2.y)
      # Drag and drop by offset
      p.dragDropRel(400, 400)
      ```
      Let me remind you that these are wrapper functions around **pyautogui** functions.
      Read more about arguments in the **pyautogui** documentation.

      ```python
      from simpleautogui import Point as P
      
      P(100, 100).click(
          oX=0, # Y offset
          oY=0, # X offset
          clicks=2, # double click
          interval=0.0, # interval between clicks in seconds
          button='right', # 'left', 'middle'
          logScreenshot=True, # screenshot logging
      )
      
      P(100, 100).moveTo(
          oX=0,
          oY=0,
          # **move_kwargs
          duration=0.0,
          logScreenshot=False,
      )
      # dragDropTo, dragDropRel same
      ```
  * ### Region
     The **Region** class represents a rectangular area on the screen.
     It allows you to perform operations within this specified area,
     like taking screenshots or searching for text.
   
     ```python
     from simpleautogui import Region
     
     # Define a region starting at x=100, y=200 with width=300 and height=400.
     r = Region(100, 200, 300, 400)
     
     # Click to the center at this region.
     r.click()
     # r.click(center=False) u can.
     
     # Move the mouse to region center.
     r.moveTo()
     # center=False u can.
     
     # Show this region (save screenshot like .png in local/temp and open it).
     r.show()
     
     # Recognizes and returns the text in the specified area of the screen.
     # We find the Tesseract-OCR path in the path variable to tesseract.exe.
     # Example with default arguments:
     r.text(
         lang: str = 'eng+rus',  # Language(s) for OCR, separated by a plus sign (e.g., 'eng+rus').
         contrast = 0,  # Level of contrast enhancement to apply to the image. 0 means no enhancement.
         resize = 0,  # Scaling factor to apply to the image. 0 means no scaling.
         sharpen = True,  # Whether to apply a sharpening filter to the image.
         **image_to_string_kwargs  # Additional keyword arguments for pytesseract.image_to_string.
     )
     # Use something like this:
     if 'some text' in r.text():
         pass
     
     # Search for text throughout the entire screen.
     # Return the list of Region objects containing the text.
     result: list[Region] = Region().findText('example')
     # With args...
     result: list[Region] = Region().findText(
         text='example',
         lang='eng+rus',
         contrast=0,
         resize=0,
         sharpen=True,
         case_sensitive=False,
         **image_to_string_kwargs
     )
     ```
  Both classes streamline the process of screen automation by providing a set of intuitive methods to interact with the GUI elements.

## Modules
## Screen
* ### **waitImage**

  Waits for a specified image or images to appear on the screen within a timeout.

  ```python
  from simpleautogui import screen

  # Waits for the image to appear and clicks on its center.
  waitImage('image.png').click()

  # Waits for one of several images to appear and clicks...
  waitImage(('image.png', 'image2.png')).click()
  ``` 
  The same function but with all the arguments.
  Subsequent functions will be shown more briefly, please read the detailed docs for more details.

  ```python
  # Same thing, but more details
  result: Region | None = waitImage(
      paths='image.png',  # Path or tuple of paths to the images to be searched.
      timeout=10000,  # Time in milliseconds to wait for the images.
      confidence=0.9,  # The confidence with which to match the images.
      error_dialog=False,  # If True, shows an error dialog if the images are not found.
      # Displays an error dialog and asks the user whether to continue exec code or stop.
      region=(0, 0, size().width, size().height),  # The region of the screen to search in.
      check_interval=100,  # Interval in milliseconds between checks.
  )
  result.click()
  ```


* ### **waitImages**

  Waits for multiple images to appear on the screen within a specified timeout.

  ```python

      from simpleautogui import screen

      images = waitImages('image.png')
      for img in images:
          img.click()
      # with args
      images: Region | [] = waitImages(
          paths='image.png',  # Path or tuple of paths to the images to be searched.
          timeout=10000,  # Time in milliseconds to wait for the images.
          confidence=0.9,  # The confidence with which to match the images.
          error_dialog=False,  # If True, shows an error dialog if the images are not found.
          region=(0, 0, size().width, size().height),  # The region of the screen to search in.
          check_interval=100,  # Interval in milliseconds between checks.
          proximity_threshold_px=2,  # Pixel distance to consider images as distinct.
          min_matches=1  # Minimum number of matches.
      )

* ### **waitColor and waitColors**

  Waits for a specified color or colors to appear on the screen within a timeout.

  ```python
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
      region=(0, 0, size().width, size().height),
      check_interval=100
  )
  if point:
      point.click()
  else:
      print("Green color not found")

  points: list[Point] = waitColors(
      color=('rgb(255, 0, 0)', '#00ff00', 'blue'),
      timeout=10000,
      confidence=0.9,
      error_dialog=False,
      region=(0, 0, size().width, size().height),
      check_interval=100,
      proximity_threshold_px=2,
      min_matches=0  # if 0 return all founded else count first founded
  )
  if points:
      for point in points:
          point.click()
  else:
      print("Specified colors not found")
  ```


