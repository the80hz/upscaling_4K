import os
import shutil
import subprocess
import time

from win32com import client
from  win32gui import GetWindowText, GetForegroundWindow, SetForegroundWindow, EnumWindows
from win32process import GetWindowThreadProcessId


class ActivateVenv:

    def set_cmd_to_foreground(self, hwnd, extra):
        """sets first command prompt to forgeround"""

        if "cmd.exe" in GetWindowText(hwnd):
            SetForegroundWindow(hwnd)
            return

    def get_pid(self):
        """gets process id of command prompt on foreground"""

        window = GetForegroundWindow()
        return GetWindowThreadProcessId(window)[1]

    def activate_venv(self, shell, venv_location):
        """activates venv of the active command prompt"""

        shell.AppActivate(self.get_pid())
        shell.SendKeys("cd \ {ENTER}")
        shell.SendKeys(r"cd %s {ENTER}" % venv_location)
        shell.SendKeys("activate {ENTER}")

    def run_py_script(self,shell):
        """runs the py script"""

        shell.SendKeys("cd ../..{ENTER}")
        shell.SendKeys("python run.py {ENTER}")

    def open_cmd(self, shell):
        """ opens cmd """

        shell.run("cmd.exe")
        time.sleep(1)


if __name__ == '__main__':
    print(
        "For the program to work, you need at least 200 GB for one episode of anime, and up to 1 TB for a movie.")
    print('Also make sure you have at least an RTX 2000 series graphics card.')
    work_dir = input('Enter directory: ')
    orig_path = input('Enter the full path of the original file: ')

    print('Creating folders...')
    os.mkdir(f'{work_dir}\pic1x')
    os.mkdir(f'{work_dir}\pic2x')

    # open new cmd window and run ffmpeg
    print('Converting to png...')




    os.system(f'ffmpeg -y -hide_banner -i {orig_path} {work_dir}\pic1x\%06d.png')

    # E:\test
    # "E:\test\[anti-raws]Fate Apocrypha ep.22[BDRemux].mkv"






    # delete files that are not needed



