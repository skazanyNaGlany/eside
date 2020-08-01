#!python

import sys
import os
import re
import subprocess
import base64

from typeguard import typechecked
from typing import List, Optional, Dict

from PySide2.QtWidgets import ( # pylint: disable=no-name-in-module
    QApplication, 
    QDialog, 
    QLineEdit, 
    QPushButton, 
    QVBoxLayout, 
    QListWidget, 
    QLabel
)
from PySide2 import QtCore, QtGui
from PySide2.QtCore import Qt           # pylint: disable=no-name-in-module
from PySide2.QtGui import QKeyEvent     # pylint: disable=no-name-in-module


if __name__ != '__main__':
    print('Do not import this file, just run.')
    exit(1)

if sys.version_info[0] < 3 or sys.version_info[1] < 5:
    print('Python 3.5+ is required.')
    exit(2)


APP_NAME = 'EmuFront v0.1'
APP_ICON = 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACcElEQVRYR+1WP2/TUBD/3YuctCoLMBRSBpaGCRBEIgnwDVBBkHgoAwtSPwCdmnToULtT+wGQWBjo4EQIEN8ASIIUEDCRTkg0CgOwULWOlXfISR0cy7HiRAJV5Lb37t7d791/wj8mCmP/TlI7zRE6C6D+9G3+u/vt7Sv6SQCJttX68vz9WmNYvaEAqGn9AQibUspcqbpachvJptazQogiGMtGJb81ATC0B9SMbjCjXqzkC36P7l7fOG61+WGHx5gH4SKAMoBdj/wcgAwYH0DYsXlKhJaevFr56ac3l9Y1IiRIzejM4DfFcuGan+DNS2vx2FTUa2yoD5oHrblBCZnLaK8JdDUQgJrWagDFQTg1lEWvEKMJcMOoFJJeViAA2+2/9szpWCxaG9m4Y5HRNM1W8thMbN8djkAAdl4AyI3068GPikY5rzrsIwiAUWfQC+cHRLwIIH54bjDTdo8HXgAh4XHG2B7wVdCtzv4qGhDCCQB/D9iNRlGU8yJCj1wxOwFgepgYhgjBPoAfjk7Z5vuWZX3qTEM1tZGE4Gd/EwAk3TKqKzXfcRwmiUJ4oC8EfyrGp3EMAFCWUm464kKQBtC57pk/S8m9YSaEWO4Mpn4aG8C4jXEC4Ah5wBnHna1mKjYrwO/cCSAZS5bZeum+U2LRG4LQ3ZwOSYIuWwfmN/voHceBVeBW4rcRBW7FrsdBG9EEQKAHsun1BQExbwsRQUimvp2QWT4uVQsf3aHKprQLROKe+04QN5kh7TsJuVOqrPb2iTCdcNco58+M0oXUjP4VgL2u2zRyGf6HANx9YCaqtLerhU4th6XFlDa717IiQX3gN5ut9bMIHLdqAAAAAElFTkSuQmCC'
APP_MAIN_WINDOW_WIDTH = 480
APP_MAIN_WINDOW_HEIGHT = 600

RomPathName = Dict[str, str]


def typechecked_class_decorator(exclude=None):
    if not exclude:
        exclude = []

    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and attr not in exclude:
                setattr(cls, attr, typechecked(getattr(cls, attr)))
        return cls
    return decorate


@typechecked_class_decorator()
class PCSX2Emulator:
    OPL_REGEX = '^[A-Z]{4}_[0-9]{3}.[0-9]{2}.'


    def __init__(self,
        exe_path: Optional[str] = None,
        roms_path: Optional[str] = None
    ):
        self._exe_path = exe_path
        self._roms_path = roms_path
        self._running_rom = None


    def get_emulator_roms(self) -> RomPathName:
        roms = {}

        with os.scandir(self._roms_path) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    name = entry.name

                    if not name.endswith('.iso'):
                        continue

                    if name.lower().endswith('.iso'):
                        name = name[:-4]

                    if re.match(self.OPL_REGEX, name) is not None:
                        roms[entry.path] = name[12:]
                    else:
                        roms[entry.path] = name

        return {k: v for k, v in sorted(roms.items(), key=lambda item: item[1])}


    def run_rom(self, rom_path: str) -> subprocess:
        self._running_rom = subprocess.Popen([self._exe_path, rom_path, '--fullscreen', '--nogui', '--fullboot'])

        return self._running_rom


@typechecked_class_decorator()
class MainWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(APP_NAME)
        self.setFixedSize(APP_MAIN_WINDOW_WIDTH, APP_MAIN_WINDOW_HEIGHT)
        # self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setWindowIcon(self._icon_from_base63(APP_ICON))

        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)

        self._layout = QVBoxLayout(self)
        self._games_list = QListWidget()
        self._run_game_button = QPushButton('Run selected game')
        self._refresh_list_button = QPushButton('Refresh list')
        self._settings_button = QPushButton('Settings')
        self._exit_button = QPushButton('Exit')

        self._settings_button.setDisabled(True)

        self._layout.addWidget(self._games_list)
        self._layout.addWidget(self._run_game_button)
        self._layout.addWidget(self._refresh_list_button)
        self._layout.addWidget(self._settings_button)
        self._layout.addWidget(self._exit_button)

        self._games_list.doubleClicked.connect(self._games_list_double_clicked)
        self._run_game_button.clicked.connect(self._run_game_button_clicked)

        self._exit_button.clicked.connect(self._exit_button_clicked)
        self._refresh_list_button.clicked.connect(self._refresh_list_button_clicked)

        # emulators
        self._pcsx2_emulator = PCSX2Emulator('C:\\Program Files (x86)\\PCSX2\\pcsx2.exe', 'D:\\games\\ps2')

        self._refresh_roms(True)


    def _refresh_roms(self, first_run:bool = False):
        self._pcsx2_roms = self._pcsx2_emulator.get_emulator_roms()

        self._games_list.clear()

        for path, name in self._pcsx2_roms.items():
            self._games_list.addItem(name)

        if first_run:
            self._games_list.setCurrentRow(0)
            self._games_list.setFocus()


    def _get_rom_by_index(self, index: int) -> str:
        return list(self._pcsx2_roms.keys())[index]


    def _exit_button_clicked(self):
        self.close()


    def _refresh_list_button_clicked(self):
        self._refresh_roms()


    def _run_selected_game(self):
        current_index = self._games_list.currentIndex()

        if current_index:
            self._pcsx2_emulator.run_rom(self._get_rom_by_index(current_index.row()))


    def _games_list_double_clicked(self):
        self._run_selected_game()


    def _run_game_button_clicked(self):
        self._run_selected_game()


    def _icon_from_base63(self, base64_str:str):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_str))
        icon = QtGui.QIcon(pixmap)

        return icon


app = QApplication(sys.argv)

main_window = MainWindow()
main_window.show()

sys.exit(app.exec_())
