#!python

import sys
import os
import re
import subprocess
import base64
import traceback
import shlex
import pathlib

import warnings
warnings.simplefilter('ignore', UserWarning)

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
DEFAULT_CONFIG = r"""
[global]
show_non_roms_emulator=0
show_non_exe_emulator=0

[emulator.epsxe]
system_name = Sony PlayStation
emulator_name = ePSXe
exe_paths = D:\games\epsxe\ePSXe.exe, epsxe\ePSXe.exe, epsxe_64/epsxe_x64, epsxe/epsxe_x64, epsxe/ePSXe
run_pattern = "{exe_path}" -loadbin "{rom_path}" -nogui
roms_paths = psx, roms\psx, D:\games\psx, D:\games\roms\psx
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)
roms_extensions = cue, ccd, img, iso, bin

[emulator.pcsx2]
system_name = Sony PlayStation 2
emulator_name = PCSX2
exe_paths = C:\Program Files (x86)\PCSX2\pcsx2.exe, pcsx2\pcsx2.exe, PCSX2/PCSX2
run_pattern = "{exe_path}" "{rom_path}" --fullscreen --nogui --fullboot
roms_paths = ps2, roms\ps2, D:\games\ps2, D:\games\roms\ps2
rom_name_remove0 = ^[A-Z]{4}_[0-9]{3}.[0-9]{2}.
rom_name_remove1 = \[[^\]]*\]
rom_name_remove2 = \(.*\)
roms_extensions = iso

[emulator.ppsspp]
system_name = Sony PlayStation Portable
emulator_name = PPSSPP
exe_paths = C:\Program Files\PPSSPP\PPSSPPWindows.exe, ppsspp/PPSSPPSDL
run_pattern = "{exe_path}" "{rom_path}" --fullscreen --escape-exit --pause-menu-exit
roms_paths = psp, roms\psp, D:\games\psp, D:\games\roms\psp
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
    CUE_BIN_RE_SIGN = r'^FILE\ \"(.*)\"\ BINARY$'

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


    def _get_roms_path(self) -> Optional[str]:
        for ipath in self.roms_paths:
            ipath = ipath.strip()

            if os.path.exists(ipath):
                return ipath

        return None


    def _file_extract_lines(self, filename: str) -> list:
        lines = []

        for iline in open(filename, 'r').readlines():
            lines.append(iline)

        return lines


    def _get_cue_bins(self, cue_pathname: str) -> list:
        bins = []

        for iline in self._file_extract_lines(cue_pathname):
            iline = iline.strip()

            match = re.findall(Emulator.CUE_BIN_RE_SIGN, iline)

            if len(match) == 1:
                bin_filename = match[0]

                if bin_filename not in bins:
                    bins.append(bin_filename)

        return bins


    def get_emulator_executable(self) -> Optional[str]:
        home_dir = pathlib.Path.home()

        for ipath in self.exe_paths:
            ipath = ipath.strip()

            if os.path.exists(ipath):
                return ipath

            home_ipath = os.path.join(home_dir, ipath)

            if os.path.exists(home_ipath):
                return home_ipath

            home_systems_ipath = os.path.join(home_dir, 'systems', ipath)

            if os.path.exists(home_systems_ipath):
                return home_systems_ipath

        return None


    def get_emulator_roms(self) -> Optional[dict]:
        roms_path = self._get_roms_path()
        roms = {}
        to_skip = []

        if not roms_path:
            return None

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

                if iextension == 'cue':
                    to_skip = list(set(to_skip) | set(self._get_cue_bins(ifile.path)))
                elif iextension == 'ccd':
                    img_filename = name + '.img'

                    if img_filename not in to_skip:
                        to_skip.append(img_filename)

                if ifile.name in to_skip:
                    continue

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
        exe_path = self.get_emulator_executable()

        if not exe_path:
            raise Exception('No emulator found')

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


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self._switch_emulator(False)
        elif event.key() == Qt.Key_Right:
            self._switch_emulator(True)
        else:
            super(MainWindow, self).keyPressEvent(event)


    def _switch_emulator(self, down: bool):
        emu_count = self._emu_selector.count()

        if emu_count <= 0:
            return

        current_index = self._emu_selector.currentIndex()

        if not down:
            current_index -= 1

            if current_index < 0:
                current_index = emu_count - 1
        else:
            current_index += 1

            if current_index >= emu_count:
                current_index = 0

        self._emu_selector.setCurrentIndex(current_index)


    def _show_emulators(self):
        self._emu_selector.clear()

        for iemulator in self._emulators:
            self._emu_selector.addItem('{system_name} ({emulator_name})'.format(
                system_name = iemulator.system_name,
                emulator_name = iemulator.emulator_name
            ))


    def _load_emulators(self) -> list:
        global_section_data = dict(self._config['global'].items())

        show_non_roms_emulator = global_section_data['show_non_roms_emulator'] == '1'
        show_non_exe_emulator = global_section_data['show_non_exe_emulator'] == '1'

        emulators = []

        for isection_name in self._config.sections():
            if not isection_name.startswith('emulator.'):
                continue

            isection_data = dict(self._config[isection_name].items())
            iemulator = Emulator(**isection_data)

            if not show_non_exe_emulator:
                # check if emulator executable exists
                if not iemulator.get_emulator_executable():
                    continue

            if not show_non_roms_emulator:
                # check if emulator have roms
                if not iemulator.get_emulator_roms():
                    continue

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

            emulator = self._get_current_emulator()

            if not emulator:
                return

            self._roms = self._get_current_emulator().get_emulator_roms()

            if not self._roms:
                return

            for name in self._roms.values():
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
        traceback.print_tb(x.__traceback__)
        print(str(type(x).__name__) + ': ' + str(x))

        self._message_box(str(x))


    def _run_selected_game(self):
        try:
            current_index = self._games_list.currentIndex()

            if current_index:
                current_emulator = self._get_current_emulator()

                if current_emulator:
                    rom_path = os.path.abspath(self._get_rom_by_index(current_index.row()))

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
