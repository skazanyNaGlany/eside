#!python

import sys
import os
import re
import subprocess
import base64
import traceback
import shlex
import pathlib
import shutil
import operator
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
    QMessageBox,
    QListWidgetItem
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
APP_ICON = 'iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAgAElEQVR4Xu3dT8xm533W8fu8M5lESKUIWkcF2gUgRP60my5izyKeVcKqUtWME2CD2DRsqFhUorEpDyV2kbpAZUO6QWyAxE5VqSuSBXKysJ1FNyVxEIIuWqCKSxGlC5LJzHvQ2KlIWtLHfd7rd+5z7vtjKVIW51y/+/5ev/POd2asZGn+QQABBBBAAIHpCCzT3diFEUAAAQQQQKARAEuAAAIIIIDAhAQIwISluzICCCCAAAIEwA4ggAACCCAwIQECMGHprowAAggggAABsAMIIIAAAghMSIAATFi6KyOAAAIIIEAA7AACCCCAAAITEiAAE5buyggggAACCBAAO4AAAggggMCEBAjAhKW7MgIIIIAAAgTADiCAAAIIIDAhAQIwYemujAACCCCAAAGwAwgggAACCExIgABMWLorI4AAAgggQADsAAIIIIAAAhMSIAATlu7KCCCAAAIIEAA7gAACCCCAwIQECMCEpbsyAggggAACBMAOIIAAAgggMCEBAjBh6a6MAAIIIIAAAbADCCCAAAIITEiAAExYuisjgAACCCBAAOwAAggggAACExIgABOW7soIIIAAAggQADuAAAIIIIDAhAQIwISlz3Tl+z/6T7/3G7cfvWvrO//ql559o7W2bj130HnLj33g+Se2vts7H976+ku/9g9+b+u55iGwFQECsBVpc7oQuH/3haeur9cnl9b+9BYHWJZlXddHX3z/a4++eGqn6y1mjj7j1E5XX37y1geX5dYH13Xd5GfW2tr/Xpb1S5999blXRufrfvMS2ORjmhevm/cm8BNPPv/M1XL1XGvrD290loePrr/5oR/50voFApAh/lgAfv0Dy9O3rt7x+dba7Uzq2ZQvX6/rP/nl15598eyTHkDgoAQIwEGLc+y3R4AAvD1Oe36KAOy5HWc7MgECcOT2nP0sAQJwFtHuHyAAu6/IAQ9KgAActDjHfnsE3hKA5R+21t7/9t648VP+CuDGCL8zgACEgYpD4FsECIBVGJoAATh+vQTg+B26wT4JEIB99uJUIQIEIASyYwwB6Ajf6KEJEICh63U5/w7A8XeAABy/QzfYJwECsM9enCpEgACEQHaMIQAd4Rs9NAECMHS9LkcAjr8DBOD4HbrBPgkQgH324lQhAgQgBLJj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'
APP_MAIN_WINDOW_WIDTH = 480
APP_MAIN_WINDOW_HEIGHT = 500
APP_URL = 'https://github.com/skazanyNaGlany/eside'
DEFAULT_CONFIG_PATHNAME = 'eside.ini'
DEFAULT_CONFIG = r"""
[global]
show_non_roms_emulator=1
show_non_exe_emulator=1
show_emulator_name=0
show_emulator_roms_count=0
sort_emulators=1
default_emulator=emulator.epsxe

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

[emulator.dolphin]
system_name = Nintendo GameCube
emulator_name = Dolphin
exe_paths = D:\games\Dolphin-x64\Dolphin.exe, Dolphin-x64\Dolphin.exe, dolphin-emu
run_pattern = "{exe_path}" -b -e "{rom_path}"
roms_paths = gc, roms\gc, D:\games\gc, D:\games\roms\gc
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)
roms_extensions = iso

[emulator.dolphin2]
system_name = Nintendo Wii
emulator_name = Dolphin
exe_paths = D:\games\Dolphin-x64\Dolphin.exe, Dolphin-x64\Dolphin.exe, dolphin-emu
run_pattern = "{exe_path}" -b -e "{rom_path}"
roms_paths = wii, roms\wii, D:\games\wii, D:\games\roms\wii
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)
roms_extensions = iso

[emulator.cemu]
system_name = Nintendo Wii U
emulator_name = Cemu
exe_paths = D:\games\cemu\Cemu.exe, cemu\Cemu.exe
run_pattern = "{exe_path}" -f -g "{rom_path}"
roms_paths = wiiu, roms\wiiu, D:\games\wiiu, D:\games\roms\wiiu
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)
roms_extensions = wud, wux, iso, wad, rpx

[emulator.redream]
system_name = Sega Dreamcast
emulator_name = Redream
exe_paths = D:\games\redream\redream.exe, redream\redream.exe, redream\redream
run_pattern = "{exe_path}" "{rom_path}"
roms_paths = dreamcast, roms\dreamcast, D:\games\dreamcast, D:\games\roms\dreamcast
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)
roms_extensions = cdi, chd, gdi

[emulator.xenia]
system_name = Microsoft XBox 360
emulator_name = Xenia
exe_paths = D:\games\xenia\xenia.exe, xenia\xenia.exe
run_pattern = "{exe_path}" "{rom_path}" --fullscreen
roms_paths = x360, roms\x360, D:\games\x360, D:\games\roms\x360
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)
roms_extensions = iso, xex, xcp, *
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
class Utils:
    @staticmethod
    def file_write_lines(filename: str, lines: list, cr_lf: bool = True):
        ending = '\r\n' if cr_lf else '\n'
        processed_lines = ending.join([iline.strip()  for iline in lines]) + ending

        with open(filename, 'w', newline='') as f:
            f.write(processed_lines)


    @staticmethod
    def file_extract_lines(filename: str) -> list:
        lines = []

        for iline in open(filename, 'r').readlines():
            lines.append(iline)

        return lines


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
        internal_name: str,
        **kwargs
    ):
        self.system_name = system_name.strip()
        self.emulator_name = emulator_name.strip()
        self.exe_paths = exe_paths.strip().replace('\\', os.sep).split(',')
        self.run_pattern = run_pattern.strip()
        self.roms_paths = roms_paths.strip().replace('\\', os.sep).split(',')
        self.rom_name_remove = []
        self.roms_extensions = roms_extensions.strip().split(',')
        self.internal_name = internal_name
        self._cached_roms = None
        self._cached_exe_pathname = None

        for ikey in kwargs:
            if ikey.startswith('rom_name_remove'):
                self.rom_name_remove.append(kwargs[ikey].strip())


    def _get_roms_path(self) -> Optional[str]:
        for ipath in self.roms_paths:
            ipath = ipath.strip()

            if os.path.exists(ipath):
                return ipath

        return None


    def _get_cue_bins(self, cue_pathname: str) -> list:
        bins = []

        for iline in Utils.file_extract_lines(cue_pathname):
            iline = iline.strip()

            match = re.findall(Emulator.CUE_BIN_RE_SIGN, iline)

            if len(match) == 1:
                bin_filename = match[0]

                if bin_filename not in bins:
                    bins.append(bin_filename)

        return bins


    def _raise_no_exe_exception(self):
        raise Exception('No emulator executable for {system_name} ({emulator_name}) found'.format(
            system_name=self.system_name,
            emulator_name=self.emulator_name
        ))


    def get_emulator_executable(self, cached: bool = True) -> Optional[str]:
        if cached and self._cached_exe_pathname is not None:
            return self._cached_exe_pathname

        home_dir = pathlib.Path.home()
        exe_pathname = None
        already_checked = []

        for ipath in self.exe_paths:
            ipath = ipath.strip()

            # just search in path provided in config
            if os.path.exists(ipath):
                exe_pathname = ipath
                break

            # search in dome directory
            home_ipath = os.path.join(home_dir, ipath)

            if os.path.exists(home_ipath):
                exe_pathname = home_ipath
                break

            # search in home + /systems/ directory
            home_systems_ipath = os.path.join(home_dir, 'systems', ipath)

            if os.path.exists(home_systems_ipath):
                exe_pathname = home_systems_ipath
                break

            # search in system's PATH
            ipath_basename = os.path.basename(ipath)

            if ipath_basename not in already_checked:
                already_checked.append(ipath_basename)

                path_exe_pathname = shutil.which(ipath_basename)

                if path_exe_pathname:
                    exe_pathname = path_exe_pathname
                    break

        self._cached_exe_pathname = exe_pathname

        return exe_pathname


    def get_emulator_roms(self, cached: bool = True) -> Optional[dict]:
        roms_path = self._get_roms_path()
        roms = {}
        to_skip = []

        if cached and self._cached_roms is not None:
            return self._cached_roms

        if not roms_path:
            return None

        files = list(pathlib.Path(roms_path).rglob('*'))

        for iextension in self.roms_extensions:
            iextension = iextension.strip()

            iextension_full = '.' + iextension if iextension != '*' else ''
            iextension_full_len = len(iextension_full)

            for ifile in files:
                ifile_pathname = str(ifile)

                if ifile_pathname in roms:
                    continue

                if ifile.name.startswith('.') or not ifile.is_file():
                    continue

                lower_filename = ifile.name.lower()

                if iextension_full and (not lower_filename.endswith(iextension_full)):
                    continue

                clean_name = ifile_pathname.replace(roms_path + os.path.sep, '', 1).split(os.path.sep)[0]

                if iextension_full and clean_name.endswith(iextension_full):
                    clean_name = clean_name[:iextension_full_len * -1]

                if iextension == 'cue':
                    to_skip = list(set(to_skip) | set(self._get_cue_bins(ifile_pathname)))
                elif iextension == 'ccd':
                    img_filename = clean_name + '.img'

                    if img_filename not in to_skip:
                        to_skip.append(img_filename)

                if ifile.name in to_skip:
                    continue

                for ire in self.rom_name_remove:
                    if not ire:
                        continue

                    clean_name = re.sub(ire, '', clean_name)

                roms[ifile_pathname] = clean_name.strip()

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

        self._cached_roms = {k: v for k, v in sorted(roms.items(), key=lambda item: item[1])}
        return self._cached_roms


    def run_rom(self, rom_path: str) -> subprocess:
        exe_path = self.get_emulator_executable()

        if not exe_path:
            self._raise_no_exe_exception()

        run_command = self.run_pattern.format(exe_path = exe_path, rom_path = rom_path)
        args = shlex.split(run_command)

        self._running_rom = subprocess.Popen(args)

        return self._running_rom


    def run_gui(self) -> subprocess:
        exe_path = self.get_emulator_executable()

        if not exe_path:
            self._raise_no_exe_exception()

        run_command = '"{exe_path}"'.format(exe_path=exe_path)
        args = shlex.split(run_command)

        self._running_rom = subprocess.Popen(args)

        return self._running_rom


@typechecked_class_decorator()
class MainWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(APP_MAIN_WINDOW_WIDTH, APP_MAIN_WINDOW_HEIGHT)
        self.setWindowIcon(self._icon_from_base64(APP_ICON))
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        self._layout = QVBoxLayout(self)
        self._emu_selector = QComboBox()
        self._games_list = QListWidget()
        self._run_game_button = QPushButton('Run selected game')
        self._run_emulator_gui_button = QPushButton('Run emulator GUI')
        self._refresh_list_button = QPushButton('Refresh list')
        self._config_button = QPushButton('Configuration')
        self._about_button = QPushButton('About')
        self._exit_button = QPushButton('Exit')

        self._layout.addWidget(self._emu_selector)
        self._layout.addWidget(self._games_list)
        self._layout.addWidget(self._run_game_button)
        self._layout.addWidget(self._run_emulator_gui_button)
        self._layout.addWidget(self._refresh_list_button)
        self._layout.addWidget(self._config_button)
        self._layout.addWidget(self._about_button)
        self._layout.addWidget(self._exit_button)

        self._config = self._parse_config()
        self._config_global_section = dict(self._config['global'].items())

        self._emulators = self._load_emulators()

        self._show_emulators()
        self._show_current_emulator_roms(True)

        self._emu_selector.currentIndexChanged.connect(self._emu_selector_current_index_changed)
        self._games_list.doubleClicked.connect(self._games_list_double_clicked)
        self._run_game_button.clicked.connect(self._run_game_button_clicked)
        self._run_emulator_gui_button.clicked.connect(self._run_emulator_gui_button_clicked)
        self._about_button.clicked.connect(self._about_button_clicked)
        self._config_button.clicked.connect(self._config_button_clicked)
        self._exit_button.clicked.connect(self._exit_button_clicked)
        self._refresh_list_button.clicked.connect(self._refresh_list_button_clicked)

        self._adjust_gui()


    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Left:
            self._switch_emulator(False)
        elif key == Qt.Key_Right:
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
        self._update_current_emulator_tooltip()


    def _adjust_gui(self):
        show_emulator_name = self._config_global_section['show_emulator_name'] == '1'
        show_emulator_roms_count = self._config_global_section['show_emulator_roms_count'] == '1'

        if show_emulator_name or show_emulator_roms_count:
            self._emu_selector.setFont(QtGui.QFont('Terminal', 10))


    def _format_emulator_name(self, iemulator:Emulator) -> str:
        show_emulator_name = self._config_global_section['show_emulator_name'] == '1'
        show_emulator_roms_count = self._config_global_section['show_emulator_roms_count'] == '1'

        if show_emulator_name or show_emulator_roms_count:
            formatted_name = '{system_name:<50}'.format(system_name=iemulator.system_name)

            if show_emulator_name:
                formatted_name += '{emulator_name:<10}'.format(emulator_name=iemulator.emulator_name)

            if show_emulator_roms_count:
                formatted_name += '{roms_count}'.format(roms_count = len(iemulator.get_emulator_roms()))
        else:
            formatted_name = '{system_name}'.format(system_name=iemulator.system_name)

        return formatted_name


    def _update_current_emulator_tooltip(self):
        current_index = self._emu_selector.currentIndex()

        if current_index <= -1:
            return None

        exe_pathname = self._emulators[current_index].get_emulator_executable()

        if exe_pathname:
            self._emu_selector.setToolTip(exe_pathname)
        else:
            self._emu_selector.setToolTip('')


    def _show_emulators(self):
        default_emulator = self._config_global_section['default_emulator'].strip()
        default_emulator_index = -1

        self._emu_selector.clear()

        for iemulator in self._emulators:
            self._emu_selector.addItem(self._format_emulator_name(iemulator))

            if default_emulator and default_emulator_index == -1 and iemulator.internal_name == default_emulator:
                default_emulator_index = self._emulators.index(iemulator)

        if default_emulator_index != -1:
            self._emu_selector.setCurrentIndex(default_emulator_index)

        self._update_current_emulator_tooltip()


    def _load_emulators(self) -> list:
        show_non_roms_emulator = self._config_global_section['show_non_roms_emulator'] == '1'
        show_non_exe_emulator = self._config_global_section['show_non_exe_emulator'] == '1'
        sort_emulators = self._config_global_section['sort_emulators'] == '1'

        emulators = []

        for isection_name in self._config.sections():
            if not isection_name.startswith('emulator.'):
                continue

            isection_data = dict(self._config[isection_name].items())
            iemulator = Emulator(**isection_data, internal_name=isection_name)

            if not show_non_exe_emulator:
                # check if emulator executable exists
                if not iemulator.get_emulator_executable():
                    continue

            if not show_non_roms_emulator:
                # check if emulator have roms
                if not iemulator.get_emulator_roms():
                    continue

            emulators.append(iemulator)

        if sort_emulators:
            emulators = sorted(emulators, key=operator.attrgetter('system_name'))

        return emulators


    def _message_box(self, text: str, error:bool = True):
        msg = QMessageBox()
        msg.setTextFormat(Qt.RichText)
        msg.setWindowTitle(APP_NAME)
        msg.setText(text)

        if error:
            msg.setIcon(QMessageBox.Critical)

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


    def _show_current_emulator_roms(self, first_run:bool = False, cached:bool = True):
        try:
            self._games_list.clear()

            emulator = self._get_current_emulator()

            if not emulator:
                return

            self._roms = self._get_current_emulator().get_emulator_roms(cached)

            if not self._roms:
                return

            for pathname, name in self._roms.items():
                item = QListWidgetItem(name)
                item.setToolTip(pathname)

                self._games_list.addItem(item)

            if first_run:
                self._games_list.setCurrentRow(0)
                self._games_list.setFocus()
        except Exception as x:
            self._message_box(str(x))


    def _get_rom_by_index(self, index: int) -> Optional[str]:
        if not self._roms:
            return None

        return list(self._roms.keys())[index]


    def _exit_button_clicked(self):
        self.close()


    def _refresh_list_button_clicked(self):
        self._show_current_emulator_roms(cached=False)


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
                    rom_path = self._get_rom_by_index(current_index.row())

                    if not rom_path:
                        return

                    rom_full_path = os.path.abspath(rom_path)

                    print('Running rom: ' + rom_full_path)
                    current_emulator.run_rom(rom_full_path)
        except Exception as x:
            self._log_exception(x)


    def _games_list_double_clicked(self):
        self._run_selected_game()


    def _emu_selector_current_index_changed(self, index):
        self._show_current_emulator_roms(True)
        self._update_current_emulator_tooltip()


    def _run_game_button_clicked(self):
        self._run_selected_game()


    def _run_emulator_gui_button_clicked(self):
        try:
            current_emulator = self._get_current_emulator()

            if current_emulator:
                current_emulator.run_gui()
        except Exception as x:
            self._log_exception(x)


    def _about_button_clicked(self):
        msg = r'''
            {APP_NAME}<br><br>
            <a href='{APP_URL}' style="text-decoration: none;">{APP_URL}</a>
        '''.format(APP_NAME=APP_NAME, APP_URL=APP_URL)

        self._message_box(msg, False)


    def _config_button_clicked(self):
        target_config_pathname = os.path.join(os.getcwd(), DEFAULT_CONFIG_PATHNAME)

        if not os.path.exists(DEFAULT_CONFIG_PATHNAME):
            try:
                Utils.file_write_lines(
                    DEFAULT_CONFIG_PATHNAME,
                    DEFAULT_CONFIG.strip().splitlines(False)
                )

                self._message_box('Configuration file written to ' + target_config_pathname, False)
            except:
                self._message_box('Cannot write configuration file to ' + target_config_pathname, True)
                return

        os.system(target_config_pathname)


    def _icon_from_base64(self, base64_str:str):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_str))
        icon = QtGui.QIcon(pixmap)

        return icon


app = QApplication(sys.argv)

main_window = MainWindow()
main_window.show()

sys.exit(app.exec_())
