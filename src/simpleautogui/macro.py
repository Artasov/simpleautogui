from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from threading import Event, Lock, Thread
from typing import Callable

from simpleautogui.screen.classes.base import Point, Region


class MacroStopped(Exception):
    """Raised inside a macro when cooperative stop is requested."""


class MacroState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPING = "stopping"


class MacroContext:
    """Runtime context passed to a macro execution."""

    def __init__(self, stop_event: Event):
        self._stop_event = stop_event

    @property
    def is_stop_requested(self) -> bool:
        return self._stop_event.is_set()

    @property
    def is_running(self) -> bool:
        return not self.is_stop_requested

    def stop(self) -> None:
        self._stop_event.set()

    def check_stop(self) -> None:
        if self.is_stop_requested:
            raise MacroStopped()

    def sleep(self, seconds: int | float, check_interval: int | float = 0.05) -> None:
        self._check_positive_interval(check_interval, "check_interval")
        end_time = float(seconds)
        if end_time <= 0:
            self.check_stop()
            return

        elapsed = 0.0
        while elapsed < end_time:
            self.check_stop()
            step = min(float(check_interval), end_time - elapsed)
            if self._stop_event.wait(step):
                raise MacroStopped()
            elapsed += step

    def wait_image(
            self,
            region: Region,
            paths: str | tuple[str, ...] | list[str],
            timeout: int | float = 10,
            confidence: float = 0.9,
            check_interval: int | float = 0.1,
            error_dialog: bool = False,
    ) -> Region | None:
        self._check_positive_interval(check_interval, "check_interval")
        self.check_stop()
        elapsed = 0.0
        while elapsed <= timeout:
            self.check_stop()
            result = region.wait_image(
                paths=paths,
                timeout=0,
                confidence=confidence,
                error_dialog=False,
                check_interval=check_interval,
            )
            if result is not None:
                return result

            if timeout == 0:
                break
            step = min(float(check_interval), float(timeout) - elapsed)
            if step <= 0:
                break
            self.sleep(step, check_interval=step)
            elapsed += step

        if error_dialog:
            region.wait_image(paths, timeout=0, confidence=confidence, error_dialog=True)
        return None

    def wait_images(
            self,
            region: Region,
            paths: str | tuple[str, ...] | list[str],
            timeout: int | float = 10,
            confidence: float = 0.9,
            check_interval: int | float = 0.1,
            proximity_threshold_px: int = 2,
            min_matches: int = 1,
            error_dialog: bool = False,
    ) -> list[Region]:
        self._check_positive_interval(check_interval, "check_interval")
        self.check_stop()
        elapsed = 0.0
        while elapsed <= timeout:
            self.check_stop()
            result = region.wait_images(
                paths=paths,
                timeout=0,
                confidence=confidence,
                error_dialog=False,
                check_interval=check_interval,
                proximity_threshold_px=proximity_threshold_px,
                min_matches=min_matches,
            )
            if result:
                return result

            if timeout == 0:
                break
            step = min(float(check_interval), float(timeout) - elapsed)
            if step <= 0:
                break
            self.sleep(step, check_interval=step)
            elapsed += step

        if error_dialog:
            region.wait_images(paths, timeout=0, confidence=confidence, error_dialog=True)
        return []

    def wait_color(
            self,
            region: Region,
            color: str | tuple[int, int, int] | list[int],
            timeout: int | float = 10,
            confidence: float = 0.9,
            check_interval: int | float = 0.1,
            error_dialog: bool = False,
    ) -> Point | None:
        self._check_positive_interval(check_interval, "check_interval")
        self.check_stop()
        elapsed = 0.0
        while elapsed <= timeout:
            self.check_stop()
            result = region.wait_color(
                color=color,
                timeout=0,
                confidence=confidence,
                error_dialog=False,
                check_interval=check_interval,
            )
            if result is not None:
                return result

            if timeout == 0:
                break
            step = min(float(check_interval), float(timeout) - elapsed)
            if step <= 0:
                break
            self.sleep(step, check_interval=step)
            elapsed += step

        if error_dialog:
            region.wait_color(color, timeout=0, confidence=confidence, error_dialog=True)
        return None

    def wait_colors(
            self,
            region: Region,
            color: str
                   | tuple[int, int, int]
                   | list[int]
                   | tuple[str | tuple[int, int, int], ...]
                   | list[str | tuple[int, int, int]],
            timeout: int | float = 10,
            confidence: float = 0.9,
            check_interval: int | float = 0.1,
            proximity_threshold_px: int = 2,
            min_matches: int = 0,
            error_dialog: bool = False,
    ) -> list[Point] | None:
        self._check_positive_interval(check_interval, "check_interval")
        self.check_stop()
        elapsed = 0.0
        while elapsed <= timeout:
            self.check_stop()
            result = region.wait_colors(
                color=color,
                timeout=0,
                confidence=confidence,
                error_dialog=False,
                check_interval=check_interval,
                proximity_threshold_px=proximity_threshold_px,
                min_matches=min_matches,
            )
            if result:
                return result

            if timeout == 0:
                break
            step = min(float(check_interval), float(timeout) - elapsed)
            if step <= 0:
                break
            self.sleep(step, check_interval=step)
            elapsed += step

        if error_dialog:
            region.wait_colors(color, timeout=0, confidence=confidence, error_dialog=True)
        return None

    @staticmethod
    def _check_positive_interval(value: int | float, name: str) -> None:
        if value <= 0:
            raise ValueError(f"{name} must be greater than 0.")


class Macro(ABC):
    """Base class for hotkey-driven GUI automation scripts."""

    def on_start(self, context: MacroContext) -> None:
        pass

    @abstractmethod
    def run(self, context: MacroContext) -> None:
        pass

    def on_stop(self, context: MacroContext) -> None:
        pass

    def on_error(self, context: MacroContext, error: Exception) -> None:
        raise error


class MacroRunner:
    """Runs a Macro in a worker thread and controls it with optional hotkeys."""

    def __init__(
            self,
            macro: Macro | Callable[[], Macro],
            start_hotkey: str | None = None,
            stop_hotkey: str | None = None,
            toggle_hotkey: str | None = None,
            daemon: bool = True,
    ):
        self.macro = macro
        self.start_hotkey = start_hotkey
        self.stop_hotkey = stop_hotkey
        self.toggle_hotkey = toggle_hotkey
        self.daemon = daemon
        self.last_error: Exception | None = None

        self._state = MacroState.IDLE
        self._lock = Lock()
        self._stop_event = Event()
        self._thread: Thread | None = None
        self._hotkey_handles = []

    @property
    def state(self) -> MacroState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self.state == MacroState.RUNNING

    @property
    def is_stopping(self) -> bool:
        return self.state == MacroState.STOPPING

    def start(self) -> bool:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return False

            self.last_error = None
            self._stop_event = Event()
            self._state = MacroState.RUNNING
            self._thread = Thread(target=self._run_worker, daemon=self.daemon)
            self._thread.start()
            return True

    def stop(self, wait: bool = False, timeout: int | float | None = None) -> bool:
        thread = None
        with self._lock:
            if self._state == MacroState.IDLE:
                return False
            self._state = MacroState.STOPPING
            self._stop_event.set()
            thread = self._thread

        if wait and thread:
            thread.join(timeout)
        return True

    def toggle(self) -> bool:
        if self.is_running or self.is_stopping:
            return self.stop()
        return self.start()

    def wait(self, timeout: int | float | None = None) -> None:
        thread = self._thread
        if thread:
            thread.join(timeout)

    def bind_hotkeys(self) -> None:
        keyboard = self._keyboard()
        self.unbind_hotkeys()
        if self.start_hotkey:
            self._hotkey_handles.append(keyboard.add_hotkey(self.start_hotkey, self.start))
        if self.stop_hotkey:
            self._hotkey_handles.append(keyboard.add_hotkey(self.stop_hotkey, self.stop))
        if self.toggle_hotkey:
            self._hotkey_handles.append(keyboard.add_hotkey(self.toggle_hotkey, self.toggle))

    def unbind_hotkeys(self) -> None:
        if not self._hotkey_handles:
            return

        keyboard = self._keyboard()
        for handle in self._hotkey_handles:
            keyboard.remove_hotkey(handle)
        self._hotkey_handles = []

    def listen(self, exit_hotkey: str = "esc") -> None:
        self.bind_hotkeys()
        try:
            self._keyboard().wait(exit_hotkey)
        finally:
            self.stop(wait=True)
            self.unbind_hotkeys()

    def _run_worker(self) -> None:
        context = MacroContext(self._stop_event)
        macro = self._create_macro()
        try:
            macro.on_start(context)
            context.check_stop()
            macro.run(context)
        except MacroStopped:
            pass
        except Exception as error:
            self.last_error = error
            try:
                macro.on_error(context, error)
            except Exception as hook_error:
                self.last_error = hook_error
        finally:
            try:
                macro.on_stop(context)
            finally:
                with self._lock:
                    self._state = MacroState.IDLE
                    self._thread = None

    def _create_macro(self) -> Macro:
        if isinstance(self.macro, Macro):
            return self.macro
        return self.macro()

    @staticmethod
    def _keyboard():
        import keyboard

        return keyboard
