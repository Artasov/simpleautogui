Introduction to ``simpleautogui``
=====================================================================================

``simpleautogui`` is a Python library designed to automate
interaction with graphical user interfaces on Windows operating
systems through scripting. Leveraging the power of several
underlying libraries, it provides a set of tools to simulate
human interaction with the computer in a straightforward and
efficient manner.

Modules and Functionality
-------------------------

The library is organized into several modules, each providing
distinct functionalities:


* ``Base``\ : Defines the fundamental classes like ``Point`` and ``Region``
  for screen regions and coordinates.
* ``Screen``\ : Contains utilities for image and color recognition,
  waiting for elements to appear.
* ``Win``\ : Provides functions to manipulate window geometry, search
  for windows by title, and arrange windows in a grid
  pattern.

The function ``waitImage`` waits for a specific image to
appear on the screen, while waitImages handles multiple images.
``waitColor`` and ``waitColors`` perform similar operations for color
detection. The Region class allows for capturing
screenshots, finding text, and clicking within specific screen regions.
The win module's ``set_window_geometry`` enables
precise control over window size and position, essential for creating a
consistent automated environment.

This library is under the MIT License, ensuring open-source 
accessibility and the freedom to integrate it into various
projects. The combination of its robust feature set and the ease 
of use makes simpleautogui a valuable tool for
automating GUI interactions on Windows.

Dependencies
------------

``simpleautogui`` relies on the following dependencies:


* Python 3.11 or higher
* PyAutoGUI
* OpenCV-Python
* PyWin32
* PyTesseract
* Mouse
* Webcolors
* Keyboard
