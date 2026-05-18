import sys
import unittest
from pathlib import Path
from threading import Event

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

try:
    from simpleautogui.macro import Macro, MacroContext, MacroRunner, MacroState, MacroStopped
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(f'Missing optional test dependency: {exc.name}')


class CountingMacro(Macro):
    def __init__(self):
        self.started = False
        self.stopped = False
        self.iterations = 0

    def on_start(self, context: MacroContext) -> None:
        self.started = True

    def run(self, context: MacroContext) -> None:
        while context.is_running:
            self.iterations += 1
            context.sleep(0.01)

    def on_stop(self, context: MacroContext) -> None:
        self.stopped = True


class ErrorMacro(Macro):
    def run(self, context: MacroContext) -> None:
        raise ValueError('broken')

    def on_error(self, context: MacroContext, error: Exception) -> None:
        raise error


class MacroTests(unittest.TestCase):
    def test_context_check_stop_raises_macro_stopped(self):
        stop_event = Event()
        context = MacroContext(stop_event)
        stop_event.set()

        with self.assertRaises(MacroStopped):
            context.check_stop()

    def test_context_rejects_zero_check_interval(self):
        context = MacroContext(Event())

        with self.assertRaises(ValueError):
            context.sleep(1, check_interval=0)

    def test_runner_starts_and_stops_macro(self):
        macro = CountingMacro()
        runner = MacroRunner(macro)

        self.assertTrue(runner.start())
        self.assertFalse(runner.start())

        runner.stop(wait=True, timeout=1)

        self.assertEqual(runner.state, MacroState.IDLE)
        self.assertTrue(macro.started)
        self.assertTrue(macro.stopped)
        self.assertGreater(macro.iterations, 0)

    def test_runner_stores_last_error(self):
        runner = MacroRunner(ErrorMacro())

        self.assertTrue(runner.start())
        runner.wait(timeout=1)

        self.assertEqual(runner.state, MacroState.IDLE)
        self.assertIsInstance(runner.last_error, ValueError)

    def test_toggle_starts_and_requests_stop(self):
        macro = CountingMacro()
        runner = MacroRunner(macro)

        self.assertTrue(runner.toggle())
        self.assertTrue(runner.toggle())
        runner.wait(timeout=1)

        self.assertEqual(runner.state, MacroState.IDLE)


if __name__ == '__main__':
    unittest.main()
