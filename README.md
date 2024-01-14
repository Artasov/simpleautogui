# simpleautogui
**simpleautogui** is a Python library designed to 
simplify the process of GUI automation. It builds 
upon the functionalities of pyautogui and provides 
a more intuitive and user-friendly interface for 
common tasks such as waiting for images to appear 
on the screen, clicking, moving the mouse cursor,
and dragging elements. Also managing windows, 
arranging in a grid, etc. Send your pull requests, 
write issues.

## Installation
Install simpleautogui using pip:
```shell
pip install simpleautogui
```

## Fast Examples
* ### Wait for image and click center on it
    ```python
    from simpleautogui import screen as ascreen
    
    
    def foo_find():
        result = ascreen.waitImage(paths="image.png")
        if result:
            result.click()
        else:
            print("Image not found within the specified timeout.")
    
    ```
    #### Same thing but more details

    ```python
    # Same thing but more details
    from simpleautogui import screen as ascreen
    
    
    def foo_find():
        result = ascreen.wait_for_image(
            paths="path/to/your/image.png",
            timeout=10000,
            accuracy=0.9,
            error_dialog=False,  # Continue or stop
            region=(0, 0, 3840, 1440),  # Default fullscreen
            check_interval=100
        )
        if result:
            print(result)
            # Box(x=323, y=242, w=25, h=26, cx=2026, cy=355)
            result.click(  # Nothing required
                center=True,
                oX=20,
                oY=20,
                clicks=10,
                button='ESC'  # Default left mouse btn
            )
        else:
            print("Image not found within the specified timeout.")
    
    ```
* ### Arrange all windows in grid
    ```python
    from simpleautogui import windows as awindow
    
    
    def foo_all_windows_to_grid():
        awindow.arrange_windows_in_grid(
            hwnds=awindow.get_all_windows(),
            rows=3, cols=3,
            monitors=(1,) # (2,) or (1, 2) or (3,)...
        )
    ```
* ### Clipboard
    ```python
    from simpleautogui import win as awin
    print(awin.get_clipboard_text())
    ```

* ### Region text recognition
    Для использования `Region().text()` нужен `Tesseract`<br>
    https://github.com/UB-Mannheim/tesseract/wiki <br>
    Не забудьте выбрать при установке нужные языки.

## License
**simpleautogui** is licensed under [MIT License](LICENSE).