import subprocess

from simpleautogui.win.console.exceptions.base import CommandExecutionError


def cmd(command: str | list[str], timeout: int | float | None = None, cwd: str | None = None, encoding='cp866'):
    try:
        result = subprocess.run(
            command,
            shell=isinstance(command, str),
            capture_output=True,
            text=True,
            encoding=encoding,
            timeout=timeout,
            cwd=cwd,
        )
        if result.returncode != 0:
            raise CommandExecutionError(f"Command '{command}' failed with error:\n{result.stderr}")
        return result.stdout
    except subprocess.TimeoutExpired as e:
        raise CommandExecutionError(f"Command '{command}' timed out after {timeout} seconds.") from e
    except CommandExecutionError:
        raise
    except Exception as e:
        raise CommandExecutionError(f"An error occurred while executing command '{command}':\n{str(e)}")


def powershell(
        command: str,
        timeout: int | float | None = None,
        cwd: str | None = None,
        encoding='utf-8'
):
    try:
        result = subprocess.run(
            ('powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', command),
            capture_output=True,
            text=True,
            encoding=encoding,
            timeout=timeout,
            cwd=cwd,
        )
        if result.returncode != 0:
            raise CommandExecutionError(f"PowerShell command '{command}' failed with error:\n{result.stderr}")
        return result.stdout
    except subprocess.TimeoutExpired as e:
        raise CommandExecutionError(f"PowerShell command '{command}' timed out after {timeout} seconds.") from e
    except CommandExecutionError:
        raise
    except Exception as e:
        raise CommandExecutionError(f"An error occurred while executing PowerShell command '{command}':\n{str(e)}")
