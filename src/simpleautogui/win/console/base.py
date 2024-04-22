import subprocess

from simpleautogui.win.console.exceptions.base import CommandExecutionError


def cmd(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='cp1251')
        if result.returncode != 0:
            raise CommandExecutionError(f"Command '{command}' failed with error:\n{result.stderr}")
        return result.stdout
    except Exception as e:
        raise CommandExecutionError(f"An error occurred while executing command '{command}':\n{str(e)}")


def powershell(command):
    try:
        result = subprocess.run(('powershell.exe', '-Command', command), capture_output=True, text=True)
        if result.returncode != 0:
            raise CommandExecutionError(f"PowerShell command '{command}' failed with error:\n{result.stderr}")
        return result.stdout
    except Exception as e:
        raise CommandExecutionError(f"An error occurred while executing PowerShell command '{command}':\n{str(e)}")

# Пример использования
# try:
#     output = cmd("dir")
#     print("Output from cmd:")
#     print(output)
# except CommandExecutionError as e:
#     print(e)
#
# try:
#     output = powershell("ls")
#     print("Output from PowerShell:")
#     print(output)
# except CommandExecutionError as e:
#     print(e)
