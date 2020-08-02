#!python

import sys
import os
import re
import subprocess
import base64
import traceback
import shlex

from typeguard import typechecked
from typing import Optional

from PySide2.QtWidgets import ( # pylint: disable=no-name-in-module
    QApplication, 
    QDialog, 
    QLineEdit, 
    QPushButton, 
    QVBoxLayout, 
    QListWidget, 
    QLabel,
    QComboBox,
    QMessageBox
)
from PySide2 import QtCore, QtGui
from PySide2.QtCore import Qt           # pylint: disable=no-name-in-module
from PySide2.QtGui import QKeyEvent     # pylint: disable=no-name-in-module

from configparser import ConfigParser


if __name__ != '__main__':
    print('Do not import this file, just run.')
    exit(1)

if sys.version_info[0] < 3 or sys.version_info[1] < 5:
    print('Python 3.5+ is required.')
    exit(2)


APP_NAME = 'ESide v0.1'
APP_ICON = 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACcElEQVRYR+1WP2/TUBD/3YuctCoLMBRSBpaGCRBEIgnwDVBBkHgoAwtSPwCdmnToULtT+wGQWBjo4EQIEN8ASIIUEDCRTkg0CgOwULWOlXfISR0cy7HiRAJV5Lb37t7d791/wj8mCmP/TlI7zRE6C6D+9G3+u/vt7Sv6SQCJttX68vz9WmNYvaEAqGn9AQibUspcqbpachvJptazQogiGMtGJb81ATC0B9SMbjCjXqzkC36P7l7fOG61+WGHx5gH4SKAMoBdj/wcgAwYH0DYsXlKhJaevFr56ac3l9Y1IiRIzejM4DfFcuGan+DNS2vx2FTUa2yoD5oHrblBCZnLaK8JdDUQgJrWagDFQTg1lEWvEKMJcMOoFJJeViAA2+2/9szpWCxaG9m4Y5HRNM1W8thMbN8djkAAdl4AyI3068GPikY5rzrsIwiAUWfQC+cHRLwIIH54bjDTdo8HXgAh4XHG2B7wVdCtzv4qGhDCCQB/D9iNRlGU8yJCj1wxOwFgepgYhgjBPoAfjk7Z5vuWZX3qTEM1tZGE4Gd/EwAk3TKqKzXfcRwmiUJ4oC8EfyrGp3EMAFCWUm464kKQBtC57pk/S8m9YSaEWO4Mpn4aG8C4jXEC4Ah5wBnHna1mKjYrwO/cCSAZS5bZeum+U2LRG4LQ3ZwOSYIuWwfmN/voHceBVeBW4rcRBW7FrsdBG9EEQKAHsun1BQExbwsRQUimvp2QWT4uVQsf3aHKprQLROKe+04QN5kh7TsJuVOqrPb2iTCdcNco58+M0oXUjP4VgL2u2zRyGf6HANx9YCaqtLerhU4th6XFlDa717IiQX3gN5ut9bMIHLdqAAAAAElFTkSuQmCC'
APP_MAIN_WINDOW_WIDTH = 480
APP_MAIN_WINDOW_HEIGHT = 600
DEFAULT_CONFIG_PATHNAME = 'eside.ini'
DEFAULT_CONFIG = """
[global]

[emulator.epsxe]
system_name = Sony PlayStation
emulator_name = ePSXe
exe_paths = D:\games\epsxe\ePSXe.exe, epsxe\ePSXe.exe
run_pattern = "{exe_path}" -loadbin "{rom_path}" -nogui
roms_paths = psx, roms\psx, D:\games\psx
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)
roms_extensions = cue, img, iso

[emulator.pcsx2]
system_name = Sony PlayStation 2
emulator_name = PCSX2
exe_paths = C:\Program Files (x86)\PCSX2\pcsx2.exe, pcsx2\pcsx2.exe
run_pattern = "{exe_path}" "{rom_path}" --fullscreen --nogui --fullboot
roms_paths = ps2, roms\ps2, D:\games\ps2
rom_name_remove0 = ^[A-Z]{4}_[0-9]{3}.[0-9]{2}.
rom_name_remove1 = \[[^\]]*\]
rom_name_remove2 = \(.*\)
roms_extensions = iso
"""


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
class Emulator:
    def __init__(self,
        system_name: str,
        emulator_name: str,
        exe_paths: str,
        run_pattern: str,
        roms_paths: str,
        roms_extensions: str,
        **kwargs
    ):
        self.system_name = system_name.strip()
        self.emulator_name = emulator_name.strip()
        self.exe_paths = exe_paths.strip().replace('\\', os.sep).split(',')
        self.run_pattern = run_pattern.strip()
        self.roms_paths = roms_paths.strip().replace('\\', os.sep).split(',')
        self.rom_name_remove = []
        self.roms_extensions = roms_extensions.strip().split(',')

        for ikey in kwargs:
            if ikey.startswith('rom_name_remove'):
                self.rom_name_remove.append(kwargs[ikey].strip())


    def _get_roms_path(self) -> str:
        for ipath in self.roms_paths:
            ipath = ipath.strip()

            if os.path.exists(ipath):
                return ipath

        # this will throw exception if path does not exists
        return self.roms_paths[0].strip()


    def _get_exe_path(self) -> str:
        for ipath in self.exe_paths:
            ipath = ipath.strip()

            if os.path.exists(ipath):
                return ipath

        # this will throw exception if executable does not exists
        return self.exe_paths[0].strip()


    def get_emulator_roms(self) -> dict:
        roms_path = self._get_roms_path()
        roms = {}

        files = list(os.scandir(roms_path))

        for iextension in self.roms_extensions:
            iextension = iextension.strip()

            iextension_full = '.' + iextension
            iextension_full_len = len(iextension_full)

            for ifile in files:
                if ifile.path in roms:
                    continue

                if ifile.name.startswith('.') or not ifile.is_file():
                    continue

                lower_name = ifile.name.lower()

                if not lower_name.endswith(iextension_full):
                    continue

                name = ifile.name[:iextension_full_len * -1]

                for ire in self.rom_name_remove:
                    if not ire:
                        continue

                    name = re.sub(ire, '', name)

                # if self.rom_name_remove:
                #     name = re.sub(self.rom_name_remove, '', name)

                roms[ifile.path] = name.strip()

        # append (2) (3) (4) etc. to duplicated names
        roms_values = list(roms.values())
        for ientry in roms.copy():
            name = roms[ientry]
            ientry_count = roms_values.count(name)

            if ientry_count > 1:
                counter = 1

                for ientry2 in roms:
                    if roms[ientry2] == name:
                        if counter > 1:
                            roms[ientry2] = name + ' (' + str(counter) + ')'

                        counter += 1



        # with os.scandir(roms_path) as it:
        #     for entry in it:
        #         if not entry.name.startswith('.') and entry.is_file():
        #             name = entry.name

        #             if not name.endswith('.iso'):
        #                 continue

        #             if name.lower().endswith('.iso'):
        #                 name = name[:-4]

        #             if self.rom_name_remove and re.match(self.rom_name_remove, name) is not None:
        #                 roms[entry.path] = name[12:]    # todo
        #             else:
        #                 roms[entry.path] = name

        return {k: v for k, v in sorted(roms.items(), key=lambda item: item[1])}


    def run_rom(self, rom_path: str) -> subprocess:
        exe_path = self._get_exe_path()
        run_command = self.run_pattern.format(exe_path = exe_path, rom_path = rom_path)
        args = shlex.split(run_command)

        self._running_rom = subprocess.Popen(args)

        return self._running_rom


@typechecked_class_decorator()
class MainWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(APP_MAIN_WINDOW_WIDTH, APP_MAIN_WINDOW_HEIGHT)
        self.setWindowIcon(self._icon_from_base63(APP_ICON))
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        self._layout = QVBoxLayout(self)
        self._emu_selector = QComboBox()
        self._games_list = QListWidget()
        self._run_game_button = QPushButton('Run selected game')
        self._refresh_list_button = QPushButton('Refresh list')
        self._settings_button = QPushButton('Settings')
        self._exit_button = QPushButton('Exit')

        self._settings_button.setDisabled(True)

        self._layout.addWidget(self._emu_selector)
        self._layout.addWidget(self._games_list)
        self._layout.addWidget(self._run_game_button)
        self._layout.addWidget(self._refresh_list_button)
        self._layout.addWidget(self._settings_button)
        self._layout.addWidget(self._exit_button)

        self._config = self._parse_config()
        self._emulators = self._load_emulators()

        self._show_emulators()
        self._show_current_emulator_roms(True)

        self._emu_selector.currentIndexChanged.connect(self._emu_selector_current_index_changed)

        self._games_list.doubleClicked.connect(self._games_list_double_clicked)
        self._run_game_button.clicked.connect(self._run_game_button_clicked)

        self._exit_button.clicked.connect(self._exit_button_clicked)
        self._refresh_list_button.clicked.connect(self._refresh_list_button_clicked)

        # self._config = self._parse_config()
        # self._emulators = self._load_emulators()

        # self._show_emulators()
        # self._show_current_emulator_roms(True)


    def _show_emulators(self):
        self._emu_selector.clear()

        for iemulator in self._emulators:
            self._emu_selector.addItem('{system_name} ({emulator_name})'.format(
                system_name = iemulator.system_name,
                emulator_name = iemulator.emulator_name
            ))


    def _load_emulators(self) -> list:
        emulators = []

        for isection_name in self._config.sections():
            if not isection_name.startswith('emulator.'):
                continue

            isection_data = dict(self._config[isection_name].items())

            iemulator = Emulator(**isection_data)
            emulators.append(iemulator)

        return emulators


    def _message_box(self, text: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(APP_NAME)
        msg.setText(text)
        msg.exec()


    def _parse_config(self) -> ConfigParser:
        try:
            config = ConfigParser()
            config_data = DEFAULT_CONFIG

            if os.path.exists(DEFAULT_CONFIG_PATHNAME):
                config_data = open(DEFAULT_CONFIG_PATHNAME).read()

            config.read_string(config_data)

            return config
        except Exception as x:
            self._message_box(str(x))
            exit(1)


    def _get_current_emulator(self) -> Optional[Emulator]:
        current_index = self._emu_selector.currentIndex()

        if current_index <= -1:
            return None

        return self._emulators[current_index]


    def _show_current_emulator_roms(self, first_run:bool = False):
        try:
            self._games_list.clear()

            self._roms = self._get_current_emulator().get_emulator_roms()

            for path, name in self._roms.items():
                self._games_list.addItem(name)

            if first_run:
                self._games_list.setCurrentRow(0)
                self._games_list.setFocus()
        except Exception as x:
            self._message_box(str(x))


    def _get_rom_by_index(self, index: int) -> str:
        return list(self._roms.keys())[index]


    def _exit_button_clicked(self):
        self.close()


    def _refresh_list_button_clicked(self):
        self._show_current_emulator_roms()


    def _log_exception(self, x: Exception):
        x_str = str(x)

        traceback.print_tb(x.__traceback__)
        print('Exception: ' + x_str)

        self._message_box(x_str)


    def _run_selected_game(self):
        try:
            current_index = self._games_list.currentIndex()

            if current_index:
                current_emulator = self._get_current_emulator()

                if current_emulator:
                    rom_path = self._get_rom_by_index(current_index.row())

                    print('Running rom: ' + rom_path)
                    current_emulator.run_rom(rom_path)
        except Exception as x:
            self._log_exception(x)


    def _games_list_double_clicked(self):
        self._run_selected_game()


    def _emu_selector_current_index_changed(self, index):
        self._show_current_emulator_roms(True)


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
