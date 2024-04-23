# Introduction to `simpleautogui` <br>[Read the docs]()

`simpleautogui` is a Python library designed to automate
interaction with graphical user interfaces on Windows operating
systems through scripting. Leveraging the power of several
underlying libraries, it provides a set of tools to simulate
human interaction with the computer in a straightforward and
efficient manner.

## Modules
 
The library is organized into several modules, each providing
distinct functionalities:

* `Screen`: Contains convenient classes for interacting with 
  the screen, functions for image search and text recognition.
* `Win`: Provides functions to manipulate window geometry, search
  for windows by title, and arrange windows in a grid
  pattern. There are also convenient functions for executing 
  Windows console commands.

This library is under the MIT License.

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

## Classes
  `simpleautogui` provides two main classes: `Point` and `Region`,
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
    # You can initialize Point using 0 or just 1 argument, 
    # any missing arguments will be set to the current cursor position.
    
    # Click at first point
    p.click()
    # Move the mouse to 'p' point
    p.moveIn()
    # Drag and drop 'p' to 'p2'.
    p.dragTo(p2)
    # Drag and drop by offset
    p.dragRel(400, 400)
    ```
    Let me remind you that these are wrapper functions around **pyautogui** functions.
    Read more about arguments in the **pyautogui** documentation.

    ```python
    from simpleautogui import Point
    
    Point(100, 100).click(
        oX=0, # Y offset
        oY=0, # X offset
        clicks=2, # double click
        interval=0.0, # interval between clicks in seconds
        button='right', # 'left', 'middle'
        logScreenshot=True, # screenshot logging
    )
    
    Point(100, 100).moveIn(
        oX=0,
        oY=0,
        # **move_kwargs
        duration=0.0,
        logScreenshot=False,
    )
    # dragTo, dragRel same
    ```

* ### Region
   The **Region** class represents a rectangular area on the screen.
  It allows you to perform operations within this specified area,
  like taking screenshots or searching for text.

   ```python
   from simpleautogui import Region
   
   # Define a region starting at x=100, y=200 with w=300 and h=400.
   region = Region(100, 200, 300, 400)
   # or
   fullscreen = Region()
   
   # Convert to tuple
   Region().toTuple()
   # (0, 0, 1920, 1080)
   
   # Click to the center at this region.
   region.click()
   # r.click(center=False) u can.
   
   # Move the mouse to region center.
   region.moveIn()
   # center=False u can.
   # and u can use oX= and oY= offsets.
   
   # Show this region (save screenshot like .png in local/temp and open it).
   region.show()
   
   # Recognizes and returns the text in the specified area of the screen.
   # We find the Tesseract-OCR path in the path variable to tesseract.exe.
   # Example with default arguments:
   region.text(
       lang = 'eng+rus',  # Language(s) for OCR, separated by a plus sign (e.g., 'eng+rus').
       contrast = 0,  # Level of contrast enhancement to apply to the image. 0 means no enhancement.
       resize = 0,  # Scaling factor to apply to the image. 0 means no scaling.
       sharpen = True,  # Whether to apply a sharpening filter to the image.
       # **image_to_string_kwargs Additional keyword arguments for pytesseract.image_to_string.
   )
   # Use something like this:
   if 'some text' in region.text():
       pass
   
   # Search for text throughout the entire screen.
   # Return the list of Region objects containing the text.
   result = Region().findText('example')
   # With args...
   result: list[Region] = Region().findText(
       text='example',
       lang='eng+rus',
       contrast=0,
       resize=0,
       sharpen=True,
       case_sensitive=False,
       # and other **image_to_data_kwargs
   )
   
   # Filter matching regions with 10px precision
   unique_regions: list[Region] = Region.removeProximity(
      regions=(Region(), Region(), Region(), ...),
      proximity_threshold_px=10
   )
   ```

* ### Window
   `Window` is an abstraction of a window in the Windows operating system.
    It provides a convenient interface for working with windows, including getting
    information about the window title, its size and position, as well as control
    its visibility, geometry and other attributes.
    ```python
    from pprint import pprint
    from pyautogui import size
    from simpleautogui import Window
    
    # Get all visible windows.
    all_windows = Window.all()
    pprint(all_windows)
    
    # Getting a window by name (only one)  
    window = Window(title='adobe') 
    # If there are several windows, then you can select the index of the resulting window.
    window = Window(title='adobe', index=0) 
    # Or by hwnd
    window = Window(hwnd=...) 
    
    # Retrieving windows whose names contain the string 'adobe'.
    adobe_windows: list[Window] = Window.byTitle('adobe')
    
    for window in adobe_windows:
        if window.exists() and window.isVisible():
            print(window.title)
            
            # Brings the window to the front.
            window.raiseIt()
    
            # Changes the size and position of the window.
            window.setGeometry(x=0)
            window.setGeometry(x=0, y=0, w=500, h=500)
    
            # U can get the window region.
            window.region.dragTo(
                endX=1500,
                endY=size().height // 2,
                oX=window.region.w // 2, oY=15,
                center=False,
                duration=2
            )
        
            # I will not explain these functions.    
            window.maximize()
            window.minimize()
            window.restore()
            window.close()
    ```


Each of these classes streamline the process of screen automation by providing a set of intuitive methods to interact with the GUI elements.


## Special Features
* ### `waitImage` `waitImages`
   `waitImage` waits for a specified image or images to appear on the screen within a timeout.

   ```python
   from simpleautogui import Region

   # Waits for the image to appear and clicks on its center.
   Region().waitImage('image.png').click()

   # Waits for one of several images to appear and clicks...
   Region().waitImage(('image.png', 'image2.png')).click()
   ``` 
   ```python
   from simpleautogui import Region
  
   # The same function but with all the arguments.
   result: Region | None = Region().waitImage(
       paths='image.png',  # Path str or list/tuple of paths to the images to be searched.
       timeout=10,  # Time in seconds to wait for the images.
       confidence=0.9,  # The confidence with which to match the images.
       error_dialog=False,  # If True, shows an error dialog if the images are not found.
       # Displays an error dialog and asks the user whether to continue exec code or stop.
       check_interval=0.1,  # Interval in seconds between checks.
   )
   result.click()
   ```
   `waitImages` is the same thing, but can return multiple regions rather than the first matching one.
   ```python
   from simpleautogui import Region

   images = Region().waitImages('image.png')
   for img in images:
       img.click()
   
   # with args
   images: list[Region] = Region().waitImages(
       paths='image.png',
       timeout=10, 
       confidence=0.9, 
       error_dialog=False,
       check_interval=0.1,
       proximity_threshold_px=2,  # Pixel distance to consider images as distinct.
       min_matches=1  # Minimum number of matches.
   )
   ```

* ### `waitColor` `waitColors`
  Waits for a specified color or colors to appear on the screen within a timeout.
  #### NOT YET IMPLEMENTED


* ### `cmd` `powershell`
   Allows you to run `Windows` commands using `cmd` or `powershell`, 
   returns a string with console output or raise exception.   
   ```python
   from simpleautogui import cmd, powershell
   from simpleautogui.win.console.exceptions.base import CommandExecutionError
   
   try:
       output = cmd('dir')
       print(output)
   except CommandExecutionError as e:
       print(e)
   
   try:
       output = powershell('ls')
       print(output)
   except CommandExecutionError as e:
       print(e)
   ```