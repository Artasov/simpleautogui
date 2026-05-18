<div align="center">
  <h1>simpleautogui</h1>
</div>

<div align="center">
  <a href="./README.md">
    <img src="https://img.shields.io/badge/English-blue?style=for-the-badge" alt="English">
  </a>
  <a href="./README.ru.md">
    <img src="https://img.shields.io/badge/Русский-red?style=for-the-badge" alt="Русский">
  </a>
</div>

### Small Windows automation toolkit for screen, mouse, OCR, image matching, colors, windows, and shell commands

`simpleautogui` is a Python library for pragmatic Windows GUI automation.
It wraps common low-level tools like PyAutoGUI, PyWin32, Pillow, OpenCV-compatible image search, and Tesseract OCR behind a small object-oriented API.

The library is useful when a workflow is easier to automate through the real desktop than through an official API:
click a known screen point, wait for an image, read text from a region, find a color, move windows, or run a Windows command.

## Navigation

- [Installation](#installation)
- [Core concepts](#core-concepts)
- [Point](#point)
- [Region](#region)
- [OCR](#ocr)
- [Image matching](#image-matching)
- [Color matching](#color-matching)
- [Hotkey macros](#hotkey-macros)
- [Windows](#windows)
- [Window grids](#window-grids)
- [Monitors](#monitors)
- [Console commands](#console-commands)
- [Development](#development)

## Installation

```bash
pip install simpleautogui
```

Requirements:

- Python 3.11+
- Windows
- Tesseract OCR installed separately if you use OCR methods

For development:

```bash
pip install "simpleautogui[dev]"
```

## Core concepts

The public API is intentionally small:

- `Point` represents one screen coordinate.
- `Region` represents a rectangular screen area.
- `Window` wraps a native Windows window handle.
- `WindowsGrid` arranges several windows inside a region.
- `Monitor` describes available displays.
- `Macro` and `MacroRunner` run reusable automation scripts by hotkeys.
- `cmd` and `powershell` run Windows shell commands.

```python
from simpleautogui import Macro, MacroRunner, Point, Region, Window, WindowsGrid, Monitor, cmd, powershell
```

Coordinates follow the usual screen convention: `x` grows left to right, `y` grows top to bottom.
`Region(x, y, w, h)` stores width and height, not right/bottom coordinates.

## Point

Use `Point` when you already know the coordinate you want to click, move to, or drag from.

```python
from simpleautogui import Point

start = Point(100, 100)
target = Point(500, 500)

start.click()
start.move_in(duration=0.2)
start.drag_to(target, duration=0.5)
start.drag_rel(200, 0, duration=0.3)

print(start.to_tuple())  # (100, 100)
```

If `x` or `y` is omitted, the missing coordinate is taken from the current cursor position.
Zero is a valid coordinate:

```python
Point(0, 100)
Point(100, 0)
Point(None, 100)
```

Read the pixel color under a point:

```python
color = Point(100, 100).color
print(color)  # (r, g, b)
```

Wait for a mouse or keyboard input and return the cursor position:

```python
point = Point.input(button="right", timeout=10)
print(point)
```

## Region

Use `Region` when an action belongs to a rectangular screen area.

```python
from simpleautogui import Region

region = Region(100, 200, 300, 400)
fullscreen = Region()

region.click()
region.click(center=False)
region.move_in(o_x=10, o_y=5)
region.show()

print(region.to_tuple())  # (100, 200, 300, 400)
```

Drag from a region:

```python
from simpleautogui import Point, Region

panel = Region(100, 100, 400, 300)
panel.drag_to(Point(800, 300), center=True, duration=0.4)
panel.drag_rel(200, 0, center=False, duration=0.4)
```

Filter close duplicate regions:

```python
unique_regions = Region.remove_proximity(regions, proximity_threshold_px=10)
```

## OCR

OCR uses `pytesseract`. Install Tesseract OCR and make sure `tesseract.exe` is available in `PATH`, or configure `pytesseract` in your application.

Read text from a region:

```python
from simpleautogui import Region

text = Region(100, 100, 600, 200).text(
    lang="eng+rus",
    resize=2,
    contrast=1.5,
    sharpen=True,
)

if "Ready" in text:
    print("Application is ready")
```

Find a word or a phrase and get matching regions:

```python
from simpleautogui import Region

matches = Region().find_text(
    text="Export complete",
    lang="eng",
    resize=2,
    min_confidence=80,
    case_sensitive=False,
)

for match in matches:
    match.click()
```

`resize` improves OCR quality on small UI text. Returned coordinates are scaled back to the original screen coordinates.

## Image matching

Use image matching when the UI element is easier to identify by screenshot than by text.

```python
from simpleautogui import Region

button = Region().wait_image(
    paths="assets/export_button.png",
    timeout=10,
    confidence=0.9,
    check_interval=0.1,
)

if button:
    button.click()
```

Wait for one of several images:

```python
result = Region().wait_image(
    paths=("assets/ok.png", "assets/continue.png"),
    timeout=15,
)
```

Find multiple matches:

```python
icons = Region().wait_images(
    paths="assets/item.png",
    timeout=10,
    confidence=0.9,
    proximity_threshold_px=2,
    min_matches=1,
)

for icon in icons:
    icon.click()
```

## Color matching

Color matching is useful for simple UI state checks: active indicator, progress color, badge color, selected state.

```python
from simpleautogui import Region

point = Region().wait_color("red", timeout=10, confidence=0.95)

if point:
    point.click()
```

Supported color formats:

- `"#ff0000"`
- `"#f00"`
- `"rgb(255, 0, 0)"`
- `"red"`
- `(255, 0, 0)`

Find several colors:

```python
points = Region(0, 0, 800, 600).wait_colors(
    color=("#00ff00", "rgb(255, 0, 0)", "blue"),
    timeout=10,
    confidence=0.9,
    check_interval=0.1,
    proximity_threshold_px=2,
    min_matches=0,
)

if points:
    print(points[0])
```

`confidence=1` means exact match. Lower confidence increases the RGB tolerance.

## Hotkey macros

Use `Macro` when you want to start and stop an automation script from any screen with keyboard shortcuts.
The macro itself runs in a worker thread. Stop is cooperative: the runner requests stop, and the macro exits at the next `context.check_stop()`, `context.sleep(...)`, `context.wait_image(...)`, or `context.wait_color(...)` call.

```python
from simpleautogui import Macro, MacroContext, MacroRunner, Region


class ClickImagesMacro(Macro):
    def run(self, context: MacroContext) -> None:
        screen = Region()

        while context.is_running:
            button = context.wait_image(
                region=screen,
                paths=("assets/next.png", "assets/continue.png"),
                timeout=1,
                confidence=0.9,
            )

            context.check_stop()

            if button:
                button.click()
                context.sleep(0.2)


runner = MacroRunner(
    ClickImagesMacro(),
    start_hotkey="ctrl+alt+s",
    stop_hotkey="ctrl+alt+q",
)

runner.listen(exit_hotkey="esc")
```

Typical workflow:

- run the Python script once;
- press `Ctrl+Alt+S` to start the macro;
- press `Ctrl+Alt+Q` to request stop;
- press `Esc` to unbind hotkeys and exit the listener.

You can also use one toggle shortcut:

```python
runner = MacroRunner(ClickImagesMacro(), toggle_hotkey="ctrl+alt+m")
runner.listen(exit_hotkey="esc")
```

Lifecycle hooks are optional:

```python
class MyMacro(Macro):
    def on_start(self, context: MacroContext) -> None:
        print("started")

    def run(self, context: MacroContext) -> None:
        ...

    def on_stop(self, context: MacroContext) -> None:
        print("stopped")
```

If your macro uses long loops or long waits, prefer `context.sleep`, `context.wait_image`, `context.wait_images`, `context.wait_color`, and `context.wait_colors` over direct long blocking calls.
That keeps hotkey stop responsive.

## Windows

Use `Window` to find and control native Windows windows.

```python
from simpleautogui import Window

window = Window(title="Notepad")
print(window.title)
print(window.region)

window.raise_it()
window.set_geometry(x=0, y=0, w=900, h=700)
window.maximize()
window.restore()
window.minimize()
window.close()
```

Find all visible windows or filter by title:

```python
from simpleautogui import Window

for window in Window.all():
    print(window.title)

notepads = Window.by_title("notepad", case_sensitive=False)
```

## Window grids

`WindowsGrid` arranges windows inside a target region.

```python
from simpleautogui import Region, Window, WindowsGrid

windows = Window.by_title("notepad")

grid = WindowsGrid(
    windows=windows[:4],
    rows=2,
    cols=2,
    region=Region(0, 0, 1600, 900),
)

grid.arrange()
```

`append`, `prepend`, and `insert` update the window list and arrange the grid again:

```python
grid.append(Window(title="Calculator"))
grid.prepend(Window(title="Explorer"))
grid.insert(1, Window(title="Terminal"))
```

## Monitors

`Monitor` exposes full and work regions for each display.

```python
from simpleautogui import Monitor

for monitor in Monitor.all():
    print(monitor.name)
    print(monitor.fregion)  # full monitor region
    print(monitor.wregion)  # work area without taskbar
    print(monitor.flags)
    print(monitor.device)
```

## Console commands

Run Windows shell commands and get stdout as a string.

```python
from simpleautogui import cmd, powershell
from simpleautogui.win.console.exceptions.base import CommandExecutionError

try:
    print(cmd("dir", timeout=10))
    print(powershell("Get-ChildItem", timeout=10))
except CommandExecutionError as exc:
    print(exc)
```

For safer `cmd` calls, pass a list instead of a shell string:

```python
output = cmd(["cmd.exe", "/c", "dir"], timeout=10)
```

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run checks:

```bash
python -m ruff check .
python -m pytest -q
python -m build
python -m twine check dist/*
```

Release workflow is described in [RELEASE_GUIDE.md](./RELEASE_GUIDE.md).
