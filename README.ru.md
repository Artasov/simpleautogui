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

### Небольшой Windows toolkit для автоматизации экрана, мыши, OCR, поиска изображений, цветов, окон и shell-команд

`simpleautogui` — Python-библиотека для практичной автоматизации Windows GUI.
Она оборачивает PyAutoGUI, PyWin32, Pillow, OpenCV-compatible image search и Tesseract OCR в небольшой объектный API.

Библиотека полезна, когда сценарий проще автоматизировать через настоящий desktop, а не через официальный API:
кликнуть в точку, дождаться изображения, прочитать текст из области, найти цвет, разложить окна или выполнить Windows-команду.

## Навигация

- [Установка](#установка)
- [Основные сущности](#основные-сущности)
- [Point](#point)
- [Region](#region)
- [OCR](#ocr)
- [Поиск изображений](#поиск-изображений)
- [Поиск цветов](#поиск-цветов)
- [Макросы и реальное применение](#макросы-и-реальное-применение)
- [Окна](#окна)
- [Сетки окон](#сетки-окон)
- [Мониторы](#мониторы)
- [Console-команды](#console-команды)
- [Разработка](#разработка)

## Установка

```bash
pip install simpleautogui
```

Требования:

- Python 3.11+
- Windows
- Tesseract OCR устанавливается отдельно, если нужны OCR-методы

Для разработки:

```bash
pip install "simpleautogui[dev]"
```

## Основные сущности

Публичный API специально небольшой:

- `Point` — одна координата на экране.
- `Region` — прямоугольная область экрана.
- `Window` — обёртка над native Windows window handle.
- `WindowsGrid` — раскладывает несколько окон внутри области.
- `Monitor` — описывает доступные мониторы.
- `AbstractMacro` и `MacroRunner` — запускают переиспользуемые automation scripts по hotkey.
- `cmd` и `powershell` — запускают Windows shell-команды.

```python
from simpleautogui import AbstractMacro, MacroRunner, Point, Region, Window, WindowsGrid, Monitor, cmd, powershell
```

Координаты обычные экранные: `x` растёт слева направо, `y` растёт сверху вниз.
`Region(x, y, w, h)` хранит ширину и высоту, а не right/bottom координаты.

## Point

Используй `Point`, когда уже известна координата для клика, движения мыши или drag.

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

Если `x` или `y` не передан, недостающая координата берётся из текущей позиции курсора.
Ноль — валидная координата:

```python
Point(0, 100)
Point(100, 0)
Point(None, 100)
```

Прочитать цвет пикселя под точкой:

```python
color = Point(100, 100).color
print(color)  # (r, g, b)
```

Дождаться клика мыши или клавиши и вернуть позицию курсора:

```python
point = Point.input(button="right", timeout=10)
print(point)
```

## Region

Используй `Region`, когда действие относится к прямоугольной области экрана.

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

Drag из области:

```python
from simpleautogui import Point, Region

panel = Region(100, 100, 400, 300)
panel.drag_to(Point(800, 300), center=True, duration=0.4)
panel.drag_rel(200, 0, center=False, duration=0.4)
```

Отфильтровать близкие дубли областей:

```python
unique_regions = Region.remove_proximity(regions, proximity_threshold_px=10)
```

## OCR

OCR работает через `pytesseract`. Установи Tesseract OCR отдельно и добавь `tesseract.exe` в `PATH`, либо настрой `pytesseract` в своём приложении.

Прочитать текст из области:

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

Найти слово или фразу и получить области совпадений:

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

`resize` помогает OCR на мелком UI-тексте. Возвращаемые координаты пересчитываются обратно в исходные экранные координаты.

## Поиск изображений

Поиск изображений удобен, когда UI-элемент проще определить по screenshot, чем по тексту.

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

Дождаться одного из нескольких изображений:

```python
result = Region().wait_image(
    paths=("assets/ok.png", "assets/continue.png"),
    timeout=15,
)
```

Найти несколько совпадений:

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

## Поиск цветов

Поиск цвета полезен для простых проверок состояния UI: активный индикатор, цвет прогресса, badge, selected-state.

```python
from simpleautogui import Region

point = Region().wait_color("red", timeout=10, confidence=0.95)

if point:
    point.click()
```

Поддерживаемые форматы цвета:

- `"#ff0000"`
- `"#f00"`
- `"rgb(255, 0, 0)"`
- `"red"`
- `(255, 0, 0)`

Найти несколько цветов:

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

`confidence=1` означает точное совпадение. Чем ниже confidence, тем шире RGB-допуск.

## Макросы и реальное применение

Используй `AbstractMacro`, когда нужно запускать и останавливать automation script с любого экрана сочетанием клавиш.
Сам макрос выполняется в отдельном worker thread. Остановка кооперативная: runner просит остановиться, а макрос выходит на ближайшем `context.check_stop()`, `context.sleep(...)`, `context.wait_image(...)` или `context.wait_color(...)`.

```python
from simpleautogui import AbstractMacro, MacroContext, MacroRunner, Region


class ClickImagesMacro(AbstractMacro):
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


if __name__ == "__main__":
    runner = MacroRunner(
        ClickImagesMacro(),
        start_hotkey="ctrl+alt+s",
        stop_hotkey="ctrl+alt+q",
    )

    print("Ctrl+Alt+S - старт, Ctrl+Alt+Q - стоп, Esc - выход")
    runner.listen(exit_hotkey="esc")
```

Типичный сценарий:

- один раз запустить Python-скрипт;
- нажать `Ctrl+Alt+S`, чтобы стартовать макрос;
- нажать `Ctrl+Alt+Q`, чтобы запросить остановку;
- нажать `Esc`, чтобы снять hotkeys и выйти из listener.

Можно использовать один toggle-hotkey:

```python
runner = MacroRunner(ClickImagesMacro(), toggle_hotkey="ctrl+alt+m")
runner.listen(exit_hotkey="esc")
```

Lifecycle hooks необязательные:

```python
class MyMacro(AbstractMacro):
    def on_start(self, context: MacroContext) -> None:
        print("started")

    def run(self, context: MacroContext) -> None:
        ...

    def on_stop(self, context: MacroContext) -> None:
        print("stopped")
```

Если внутри макроса есть длинные циклы или ожидания, лучше использовать `context.sleep`, `context.wait_image`, `context.wait_images`, `context.wait_color` и `context.wait_colors`, а не прямые долгие blocking-вызовы.
Так hotkey stop остаётся отзывчивым.

## Окна

Используй `Window`, чтобы находить и управлять native Windows окнами.

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

Найти все видимые окна или отфильтровать по title:

```python
from simpleautogui import Window

for window in Window.all():
    print(window.title)

notepads = Window.by_title("notepad", case_sensitive=False)
```

## Сетки окон

`WindowsGrid` раскладывает окна внутри заданной области.

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

`append`, `prepend` и `insert` обновляют список окон и сразу заново раскладывают сетку:

```python
grid.append(Window(title="Calculator"))
grid.prepend(Window(title="Explorer"))
grid.insert(1, Window(title="Terminal"))
```

## Мониторы

`Monitor` отдаёт полную и рабочую область каждого дисплея.

```python
from simpleautogui import Monitor

for monitor in Monitor.all():
    print(monitor.name)
    print(monitor.fregion)  # полная область монитора
    print(monitor.wregion)  # рабочая область без taskbar
    print(monitor.flags)
    print(monitor.device)
```

## Console-команды

Запускай Windows shell-команды и получай stdout как строку.

```python
from simpleautogui import cmd, powershell
from simpleautogui.win.console.exceptions.base import CommandExecutionError

try:
    print(cmd("dir", timeout=10))
    print(powershell("Get-ChildItem", timeout=10))
except CommandExecutionError as exc:
    print(exc)
```

Для более безопасного `cmd` вызова передавай список вместо shell-строки:

```python
output = cmd(["cmd.exe", "/c", "dir"], timeout=10)
```

## Разработка

Установить dev-зависимости:

```bash
pip install -e ".[dev]"
```

Запустить проверки:

```bash
python -m ruff check .
python -m pytest -q
python -m build
python -m twine check dist/*
```

Релизный процесс описан в [RELEASE_GUIDE.md](./RELEASE_GUIDE.md).
