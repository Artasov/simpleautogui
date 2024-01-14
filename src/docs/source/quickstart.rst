Quick Start
===========

To get started with SimpleAutoGUI, install the package using pip:

.. code-block:: bash

    pip install simpleautogui

Classes
-------

SimpleAutoGUI provides two main classes: `Point` and `Region`,
which facilitate screen interaction.

Point
~~~~~

The `Point` class represents a specific location on the screen.
It provides methods to perform actions like clicking or moving
the mouse to its coordinates.

.. code-block:: python

    from simpleautogui import Point

    # Create a point at x=100, y=200
    p = Point(100, 200)

    # Click at this point
    p.click()

    # Move the mouse to this point
    p.moveTo()

Region
~~~~~~

The `Region` class represents a rectangular area on the screen.
It allows you to perform operations within this specified area,
like taking screenshots or searching for text.

.. code-block:: python

    from simpleautogui import Region

    # Define a region starting at x=100, y=200 with width=300 and height=400
    r = Region(100, 200, 300, 400)

    # Click at this region
    r.click()

    # Show this region
    r.show()

    # Find text within the region
    found_text = r.findText("example")

Both classes streamline the process of screen automation by providing a set of intuitive methods to interact with the GUI elements.

Functions
---------

.. code-block:: python

    from simpleautogui import screen, windows, win

    result: Region | None = screen.waitImage(
        paths='image.png',
        timeout=10000,
        confidence=0.9,
        error_dialog=False,
        region=(0, 0, size().width, size().height),
        check_interval=100,
    )
    result.click()

    def recognize_task_bar():
        from simpleautogui.screen.classes.common import Region
        height, width = size().height, size().width
        taskbar_region = Region(0, height-50, width, 50)
        app_region = taskbar_region.findText(text='App', config='--psm 11')[0]
        print(app_region)
        app_region.show()



Lastly, for functions:

Utility Functions:
SimpleAutoGUI also includes several utility functions that allow for
more advanced screen interaction. These include waiting for a particular
color or image to appear within a specified timeout
(waitColor, waitImage), extracting text from a region on the
screen (findText), and arranging windows in a specific layout
(arrange_windows_in_grid_by_title).

These functions extend the capability of the SimpleAutoGUI
library, providing you with tools to automate complex tasks
based on visual cues from the screen.

To utilize these functions, simply call them with the required
parameters as shown in the Quick Start examples. They can be
combined with the Point and Region classes for even more powerful
and flexible screen automation scripts.

Remember to consult the SimpleAutoGUI API documentation for
detailed information on all available classes, methods, and
functions. This will help you understand the full scope of
the library's functionality and how to best incorporate it
into your automation tasks.