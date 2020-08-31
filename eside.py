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
import glob
import fnmatch

import warnings
warnings.simplefilter('ignore', UserWarning)

from typeguard import typechecked
from typing import Optional, List

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
from PySide2.QtCore import Qt                   # pylint: disable=no-name-in-module
from PySide2.QtGui import QKeyEvent, QFont      # pylint: disable=no-name-in-module

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
systems_search_path = systems, $ProgramFiles, $Path, $PATH
roms_search_path = roms
bios_search_path = systems\bios
show_non_roms_emulator = 1
show_non_exe_emulator = 1
show_emulator_name = 0
show_emulator_roms_count = 0
sort_emulators = 1
default_emulator = emulator.mame
fix_game_title = 1

[emulator.epsxe]
system_name = Sony PlayStation
emulator_name = ePSXe
emulator_url = https://www.epsxe.com/
exe_paths = epsxe\ePSXe.exe, epsxe/epsxe_x64
roms_paths = psx
rom_basename_ignore =
run_pattern0 = "{exe_path}" -loadbin "{rom_path}" -nogui
run_pattern0_roms_extensions = *.cue, *.ccd, *.img, *.iso, *.bin
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.pcsx2]
system_name = Sony PlayStation 2
emulator_name = PCSX2
emulator_url = https://pcsx2.net/
exe_paths = pcsx2\pcsx2.exe, pcsx2/PCSX2
roms_paths = ps2
rom_basename_ignore =
run_pattern0 = "{exe_path}" "{rom_path}" --fullscreen --nogui --fullboot
run_pattern0_roms_extensions = *.iso
rom_name_remove0 = ^[A-Z]{4}_[0-9]{3}.[0-9]{2}.
rom_name_remove1 = \[[^\]]*\]
rom_name_remove2 = \(.*\)

[emulator.ppsspp]
system_name = Sony PlayStation Portable
emulator_name = PPSSPP
emulator_url = https://www.ppsspp.org/
exe_paths = PPSSPP\PPSSPPWindows.exe, ppsspp/PPSSPPSDL
roms_paths = psp
rom_basename_ignore =
run_pattern0 = "{exe_path}" "{rom_path}" --fullscreen --escape-exit --pause-menu-exit
run_pattern0_roms_extensions = *.iso
rom_name_remove0 = ^[A-Z]{4}_[0-9]{3}.[0-9]{2}.
rom_name_remove1 = \[[^\]]*\]
rom_name_remove2 = \(.*\)

[emulator.dolphin]
system_name = Nintendo GameCube
emulator_name = Dolphin
emulator_url = https://dolphin-emu.org/
exe_paths = dolphin\Dolphin.exe, dolphin-emu
roms_paths = gc
rom_basename_ignore =
run_pattern0 = "{exe_path}" -b -e "{rom_path}"
run_pattern0_roms_extensions = *.iso
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.dolphin2]
system_name = Nintendo Wii
emulator_name = Dolphin
emulator_url = https://dolphin-emu.org/
exe_paths = dolphin\Dolphin.exe, dolphin-emu
roms_paths = wii
rom_basename_ignore =
run_pattern0 = "{exe_path}" -b -e "{rom_path}"
run_pattern0_roms_extensions = *.iso
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.cemu]
system_name = Nintendo Wii U
emulator_name = Cemu
emulator_url = https://cemu.info/
exe_paths = cemu\Cemu.exe
roms_paths = wiiu
rom_basename_ignore =
run_pattern0 = "{exe_path}" -f -g "{rom_path}"
run_pattern0_roms_extensions = *.wud, *.wux, *.iso, *.wad, *.rpx
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.redream]
system_name = Sega Dreamcast
emulator_name = Redream
emulator_url = https://redream.io/
exe_paths = redream\redream.exe, redream\redream
roms_paths = dreamcast
rom_basename_ignore =
run_pattern0 = "{exe_path}" "{rom_path}"
run_pattern0_roms_extensions = *.cdi, *.chd, *.gdi
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.xenia]
system_name = Microsoft XBox 360
emulator_name = Xenia
emulator_url = https://xenia.jp/
exe_paths = xenia\xenia.exe
roms_paths = x360
rom_basename_ignore = *.log
run_pattern0 = "{exe_path}" "{rom_path}" --fullscreen
run_pattern0_roms_extensions = *.iso, *.xex, *.xcp, *
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.vba-m]
system_name = Nintendo Game Boy
emulator_name = VisualBoyAdvance-M
emulator_url = https://vba-m.com/
exe_paths = D:\games\vba-m\visualboyadvance-m.exe, vba-m\visualboyadvance-m.exe
roms_paths = gb
rom_basename_ignore =
run_pattern0 = "{exe_path}" /f "{rom_path}"
run_pattern0_roms_extensions = *.gb
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.vba-m2]
system_name = Nintendo Game Boy Color
emulator_name = VisualBoyAdvance-M
emulator_url = https://vba-m.com/
exe_paths = vba-m\visualboyadvance-m.exe
roms_paths = gbc
rom_basename_ignore =
run_pattern0 = "{exe_path}" /f "{rom_path}"
run_pattern0_roms_extensions = *.gb, *.gbc
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.vba-m3]
system_name = Nintendo Game Boy Advance
emulator_name = VisualBoyAdvance-M
emulator_url = https://vba-m.com/
exe_paths = vba-m\visualboyadvance-m.exe
roms_paths = gba
rom_basename_ignore =
run_pattern0 = "{exe_path}" /f "{rom_path}"
run_pattern0_roms_extensions = *.gba
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.mame]
system_name = Arcade
emulator_name = MAME
emulator_url = https://www.mamedev.org/
exe_paths = mame\mame64.exe, mame
roms_paths = arcade
rom_basename_ignore =
run_pattern0 = "{exe_path}" -rompath "{roms_path}" "{rom_path}"
run_pattern0_roms_extensions = *.zip
rom_name_remove0 =
rom_name_remove1 =

[emulator.fceux]
system_name = Nintendo Entertainment System
emulator_name = FCEUX
emulator_url = http://fceux.com/web/home.html
exe_paths = fceux\fceux.exe
roms_paths = nes
rom_basename_ignore =
run_pattern0 = "{exe_path}" "{rom_path}"
run_pattern0_roms_extensions = *.nes
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.snes9x]
system_name = Super Nintendo Entertainment System
emulator_name = SNES9X
emulator_url = http://www.snes9x.com/
exe_paths = snes9x\snes9x*.exe
roms_paths = snes
rom_basename_ignore =
run_pattern0 = "{exe_path}" -fullscreen "{rom_path}"
run_pattern0_roms_extensions = *.sfc, *.smc
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.project64]
system_name = Nintendo 64
emulator_name = Project64
emulator_url = https://www.pj64-emu.com/
exe_paths = project64\Project64.exe
roms_paths = n64
rom_basename_ignore =
run_pattern0 = "{exe_path}" "{rom_path}"
run_pattern0_roms_extensions = *.n64
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.desmume]
system_name = Nintendo DS
emulator_name = DeSmuME
emulator_url = http://desmume.org/
exe_paths = desmume\DeSmuME*.exe
roms_paths = nds
rom_basename_ignore =
run_pattern0 = "{exe_path}" "{rom_path}"
run_pattern0_roms_extensions = *.nds
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)
rom_name_remove2 = '^[0-9]{4}\ \-\ '

[emulator.citra]
system_name = Nintendo 3DS
emulator_name = Citra
emulator_url = https://citra-emu.org/
exe_paths = citra\nightly-mingw\citra-qt.exe
roms_paths = 3ds
rom_basename_ignore =
run_pattern0 = "{exe_path}" "{rom_path}"
run_pattern0_roms_extensions = *.3ds
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.fs-uae]
system_name = Commodore Amiga
emulator_name = FS-UAE
emulator_url = https://fs-uae.net/
exe_paths = fs-uae\System\FS-UAE\Windows\x86-64\fs-uae.exe
roms_paths = amiga
rom_basename_ignore =
x_floppy_drive_speed = 0
x_amiga_model = a1200
run_pattern0 = \"{exe_path}\" --amiga-model={x_amiga_model} {{iterate_roms:--floppy-drive-{rom_index}=\"{rom_path}\":4}} {{iterate_all_roms:--floppy-image-{rom_index}=\"{rom_path}\":20}} --fullscreen --stretch=1 --kickstart_dir=\"{bios_path}\" --floppy_drive_speed={x_floppy_drive_speed}
run_pattern0_roms_extensions = *.adf
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)
"""

# set False in production, True when developing
typechecked_class_decorator_enabled = True

def typechecked_class_decorator(exclude=None):
    if not exclude:
        exclude = []

    def decorate(cls):
        if not typechecked_class_decorator_enabled:
            return cls

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


    @staticmethod
    def string_split_strip(str_to_split:str, separator:str) -> List[str]:
        return [s.strip() for s in str_to_split.strip().split(separator) if s.strip() != '']


    @staticmethod
    def string_lreplace(pattern, sub, string):
        if string.startswith(pattern):
            return string.replace(pattern, '', 1)

        return string


    @staticmethod
    def lists_to_string(lists:list, separator:str) -> str:
        all_items = []

        for ilist in lists:
            all_items.extend(ilist)

        all_items = list(set(all_items))

        return separator.join(all_items)


@typechecked_class_decorator()
class Emulator:
    CUE_BIN_RE_SIGN = r'^FILE\ \"(.*)\"\ BINARY$'
    SIMILAR_ROM_RE_SIGN = r'\(Disk\ \d\ of\ \d\)'

    def __init__(self,
        system_name: str,
        emulator_name: str,
        emulator_url: str,
        exe_paths: List[str],
        run_patterns: List[str],
        roms_paths: List[str],
        run_patterns_roms_extensions: List[List[str]],
        rom_name_remove: List[str],
        internal_name: str,
        rom_basename_ignore: List[str],
        # globals:
        systems_search_path: List[str],
        roms_search_path: List[str],
        bios_search_path: List[str],
        custom_data: dict
    ):
        self.system_name = system_name
        self.emulator_name = emulator_name
        self.emulator_url = emulator_url
        self.exe_paths = exe_paths
        self.run_patterns = run_patterns
        self.roms_paths = roms_paths
        self.rom_name_remove = rom_name_remove
        self.run_patterns_roms_extensions = run_patterns_roms_extensions
        self.internal_name = internal_name
        self.rom_basename_ignore = rom_basename_ignore
        self.systems_search_path = systems_search_path
        self.roms_search_path = roms_search_path
        self.bios_search_path = bios_search_path
        self.custom_data = custom_data
        self._cached_roms = None
        self._cached_exe_pathname = None
        self._cached_roms_pathname = None
        self._cached_bios_pathname = None

        self._roms_config = self._parse_roms_config()


    def _get_roms_path(self, cached:bool = True) -> Optional[str]:
        if cached and self._cached_roms_pathname is not None:
            return self._cached_roms_pathname

        roms_path = None

        # by path search
        for iroms_path in self.roms_search_path:
            for ipath2 in self.roms_paths:
                ipath2_full_pathname = os.path.join(iroms_path, ipath2)

                exists = glob.glob(ipath2_full_pathname)

                if len(exists):
                    roms_path = os.path.realpath(exists[0])
                    break

            if roms_path:
                break

        self._cached_roms_pathname = roms_path

        return roms_path


    def _get_bios_path(self, cached:bool = True) -> Optional[str]:
        if cached and self._cached_bios_pathname is not None:
            return self._cached_bios_pathname

        bios_path = None

        # by path search
        for ibios_path in self.bios_search_path:
            exists = glob.glob(ibios_path)

            if len(exists):
                bios_path = os.path.realpath(exists[0])
                break

        self._cached_bios_pathname = bios_path

        return bios_path


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


    def _raise_no_rom_run_pattern_exception(self, rom_path:str):
        raise Exception('No run pattern found for rom {rom_path}'.format(
            rom_path=rom_path
        ))


    def get_emulator_executable(self, cached: bool = True) -> Optional[str]:
        if cached and self._cached_exe_pathname is not None:
            return self._cached_exe_pathname

        exe_pathname = None

        # by path search
        for isystem_path in self.systems_search_path:
            for ipath2 in self.exe_paths:
                ipath2_full_pathname = os.path.join(isystem_path, ipath2)

                exists = glob.glob(ipath2_full_pathname)

                if len(exists):
                    exe_pathname = os.path.realpath(exists[0])
                    break

                ipath2_basename = os.path.basename(ipath2)
                ipath2_full_pathname = os.path.join(isystem_path, ipath2_basename)

                exists = glob.glob(ipath2_full_pathname)

                if len(exists):
                    exe_pathname = os.path.realpath(exists[0])
                    break

            if exe_pathname:
                break

        self._cached_exe_pathname = exe_pathname

        return exe_pathname


    def _ignore_file(self, filename:str) -> bool:
        for ipattern in self.rom_basename_ignore:
            if fnmatch.fnmatch(filename, ipattern):
                return True

        return False


    def _parse_roms_config(self) -> Optional[ConfigParser]:
        roms_path = self._get_roms_path()

        if not roms_path:
            return None

        roms_ini_path = os.path.join(roms_path, 'roms.ini')

        if not os.path.exists(roms_ini_path):
            return None

        config = ConfigParser()
        config.read_string(open(roms_ini_path).read())

        return config


    def _find_rom_config(self, rom_path:str) -> Optional[dict]:
        if not self._roms_config:
            return None

        if rom_path in self._roms_config.sections():
            return dict(self._roms_config[rom_path])

        for ikey in self._roms_config.sections():
            if fnmatch.fnmatch(rom_path, ikey):
                return dict(self._roms_config[ikey])

        return None


    def _get_emulator_roms(self, roms_extensions:list) -> Optional[dict]:
        roms_path = self._get_roms_path()
        roms = {}
        to_skip = []

        if not roms_path:
            return None

        files = sorted(list(pathlib.Path(roms_path).rglob('*')))

        for iextension in roms_extensions:
            for ifile in files:
                ifile_pathname = str(ifile)

                if ifile_pathname in roms:
                    continue

                if ifile.name.startswith('.'):
                    continue

                if self._ignore_file(ifile.name):
                    continue

                lower_filename = ifile.name.lower()

                if not fnmatch.fnmatch(lower_filename, iextension):
                    continue

                rom_config = self._find_rom_config(ifile.name)

                if rom_config and 'main_rom' in rom_config and rom_config['main_rom']:
                    if rom_config['main_rom'] != ifile.name:
                        continue

                clean_name = ifile_pathname.replace(roms_path + os.path.sep, '', 1).split(os.path.sep)[0]
                (clean_name, ext) = os.path.splitext(clean_name)

                if iextension == '*.cue':
                    to_skip = list(set(to_skip) | set(self._get_cue_bins(ifile_pathname)))
                elif iextension == '*.ccd':
                    img_filename = clean_name + '.img'

                    if img_filename not in to_skip:
                        to_skip.append(img_filename)

                if ifile.name in to_skip:
                    continue

                for ire in self.rom_name_remove:
                    if not ire:
                        continue

                    clean_name = re.sub(ire, '', clean_name)

                if rom_config and 'title' in rom_config:
                    clean_name = rom_config['title']

                roms[ifile_pathname] = clean_name.strip()

        return roms


    def _fixup_game_titles(self, roms:dict) -> dict:
        for pathname in roms.copy():
            name = roms[pathname]
            parts = name.split()

            if len(parts) >= 2 and parts[1] == 'The' and parts[0][-1] == ',':
                if len(parts[0]) > 1 and parts[-2] != ',':
                    part0 = parts[0][:-1]
                    part1 = parts[1]

                    parts[0] = part1
                    parts[1] = part0

                    roms[pathname] = ' '.join(parts)

        return roms


    def _count_rom_titles(self, roms:dict) -> dict:
        # append (2) (3) (4) etc. to duplicated names
        roms_values = list(roms.values())

        for pathname in roms.copy():
            name = roms[pathname]
            ientry_count = roms_values.count(name)

            if ientry_count > 1:
                counter = 1

                for ientry2 in roms:
                    if roms[ientry2] == name:
                        if counter > 1:
                            roms[ientry2] = name + ' (' + str(counter) + ')'

                        counter += 1

        return roms


    def _sort_roms_by_name(self, roms:dict) -> dict:
        return {k: v for k, v in sorted(roms.items(), key=lambda item: item[1])}


    def _add_new_roms(self, roms:dict, new_roms:dict):
        roms_values = list(roms.values())

        for ipathname, iname in new_roms.items():
            if iname not in roms_values:
                roms[ipathname] = iname


    def get_emulator_roms(self, cached:bool = True, fixup_titles:bool = False) -> Optional[dict]:
        if cached and self._cached_roms is not None:
            return self._cached_roms

        self._roms_config = self._parse_roms_config()

        roms = {}

        for iroms_extensions in self.run_patterns_roms_extensions:
            new_roms = self._get_emulator_roms(iroms_extensions)

            if new_roms:
                self._add_new_roms(roms, new_roms)

        if fixup_titles:
            roms = self._fixup_game_titles(roms)

        roms = self._count_rom_titles(roms)
        roms = self._sort_roms_by_name(roms)

        self._cached_roms = roms
        return self._cached_roms


    def _find_rom_run_pattern(self, rom_path:str) -> Optional[str]:
        rom_path_basename = os.path.basename(rom_path.lower())

        for irun_pattern_roms_extensions in self.run_patterns_roms_extensions:
            for iextension in irun_pattern_roms_extensions:
                if fnmatch.fnmatch(rom_path_basename, iextension):
                    run_pattern_index = self.run_patterns_roms_extensions.index(irun_pattern_roms_extensions)

                    return self.run_patterns[run_pattern_index]

        return None


    def _find_similar_roms(self, rom_path:str) -> List[str]:
        dirname = os.path.dirname(rom_path)
        basename = os.path.basename(rom_path)

        (filename, extension) = os.path.splitext(basename)

        match = re.findall(Emulator.SIMILAR_ROM_RE_SIGN, basename)
        len_match = len(match)

        if len_match != 1:
            return [rom_path]

        (no_disc_filename, count) = re.subn(Emulator.SIMILAR_ROM_RE_SIGN, '', basename, 1)
        (clean_filename, extension) = os.path.splitext(no_disc_filename)

        files = glob.glob(os.path.join(dirname, '*' + extension))
        similar = []

        for ifile in files:
            ifile_basename = os.path.basename(ifile)

            if ifile_basename.startswith(clean_filename) and len(re.findall(Emulator.SIMILAR_ROM_RE_SIGN, ifile_basename)) == 1 and ifile_basename.endswith(extension):
                if ifile not in similar:
                    similar.append(ifile)

        return sorted(similar)


    def _process_extended_pattern(self, pattern:str, rom_path:str, run_pattern_data:dict) -> str:
        if '{{iterate_roms:' not in pattern:
            return pattern

        pattern_parts = shlex.split(pattern)
        similar_roms = self._find_similar_roms(rom_path)

        for index, ipattern_part in enumerate(pattern_parts):
            if not ipattern_part or not ipattern_part.endswith('}}'):
                continue

            command_parts = ipattern_part[2:-2].split(':', 3)

            if len(command_parts) != 3:
                continue

            similar_roms_copy = similar_roms.copy()

            if command_parts[0] == 'iterate_roms':
                result_str = ''

                command_data_unfilled = command_parts[1]
                command_max = int(command_parts[2])

                if command_max < 1:
                    continue

                # first rom is always at 0 index
                if len(similar_roms_copy) > command_max:
                    similar_roms_copy = similar_roms_copy[0:command_max]

                result_str += command_data_unfilled.format(rom_index=0, rom_path=rom_path) + ' '

                # avoid error when similar_roms_copy is empty (command_max=1)
                if rom_path in similar_roms_copy:
                    similar_roms_copy.remove(rom_path)

                for irom_path_index, irom_path in enumerate(similar_roms_copy):
                    result_str += command_data_unfilled.format(rom_index=irom_path_index + 1, rom_path=irom_path) + ' '

                pattern_parts[index] = result_str
            elif command_parts[0] == 'iterate_all_roms':
                result_str = ''

                command_data_unfilled = command_parts[1]
                command_max = int(command_parts[2])

                if command_max < 1:
                    continue

                # first rom is always at 0 index
                if len(similar_roms_copy) > command_max:
                    similar_roms_copy = similar_roms_copy[0:command_max]

                for irom_path_index, irom_path in enumerate(similar_roms_copy):
                    result_str += command_data_unfilled.format(rom_index=irom_path_index, rom_path=irom_path) + ' '

                pattern_parts[index] = result_str

        return shlex.join(pattern_parts).replace('\'', '')


    def run_rom(self, rom_path: str) -> subprocess:
        exe_path = self.get_emulator_executable()

        if not exe_path:
            self._raise_no_exe_exception()

        run_pattern = self._find_rom_run_pattern(rom_path)

        if not run_pattern:
            # should not get here
            self._raise_no_rom_run_pattern_exception(rom_path)

        run_pattern_data = {
            'exe_path': exe_path,
            'rom_path': rom_path,
            'roms_path': self._get_roms_path(),
            'bios_path': self._get_bios_path()
        }

        if self.custom_data:
            run_pattern_data.update(self.custom_data)

        rom_config = self._find_rom_config(os.path.basename(rom_path))

        if rom_config:
            run_pattern_data.update(rom_config)

        run_pattern = self._process_extended_pattern(run_pattern, rom_path, run_pattern_data)

        run_command = run_pattern.format(**run_pattern_data)
        print('Running command: ' + run_command)

        args = shlex.split(run_command)

        self._running_rom = subprocess.Popen(args, cwd=os.path.dirname(exe_path))

        return self._running_rom


    def run_gui(self) -> subprocess:
        exe_path = self.get_emulator_executable()

        if not exe_path:
            self._raise_no_exe_exception()

        run_command = '"{exe_path}"'.format(exe_path=exe_path)
        args = shlex.split(run_command)

        self._running_rom = subprocess.Popen(args, cwd=os.path.dirname(exe_path))

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
        self._message_label = QLabel()
        self._run_game_button = QPushButton('Run selected game')
        self._run_emulator_gui_button = QPushButton('Run emulator GUI')
        self._refresh_list_button = QPushButton('Refresh list')
        self._config_button = QPushButton('Configuration')
        self._about_button = QPushButton('About')
        self._exit_button = QPushButton('Exit')

        self._message_label.setStyleSheet('background-color: white; border: 1px ridge gray; padding: 15px;')
        self._message_label.setOpenExternalLinks(True)
        self._message_label.setWordWrap(True)
        self._message_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self._message_label.setFont(QFont('Arial', 11))

        self._layout.addWidget(self._emu_selector)
        self._layout.addWidget(self._games_list)
        self._layout.addWidget(self._message_label)
        self._layout.addWidget(self._run_game_button)
        self._layout.addWidget(self._run_emulator_gui_button)
        self._layout.addWidget(self._refresh_list_button)
        self._layout.addWidget(self._config_button)
        self._layout.addWidget(self._about_button)
        self._layout.addWidget(self._exit_button)

        self._config = self._parse_config()
        self._config_global_section = dict(self._config['global'].items())

        self._systems_search_path = self._prepare_search_paths(self._config_global_section['systems_search_path'])
        self._roms_search_path = self._prepare_search_paths(self._config_global_section['roms_search_path'])
        self._bios_search_path = self._prepare_search_paths(self._config_global_section['bios_search_path'])
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
        self._show_warning_message()


    def _show_warning_message(self):
        current_index = self._emu_selector.currentIndex()

        if current_index <= -1:
            return None

        emulator = self._emulators[current_index]

        exe_pathname = emulator.get_emulator_executable()
        roms = emulator.get_emulator_roms()

        if exe_pathname and roms:
            self._show_message('')
            return

        if not exe_pathname:
            systems_first_pathname = emulator.systems_search_path[0] if emulator.systems_search_path else ''
            emulator_first_pathname = emulator.exe_paths[0].split(os.path.sep)[0] if emulator.exe_paths else ''

            emulator_pathname = os.path.realpath(os.path.join(systems_first_pathname, emulator_first_pathname) if (systems_first_pathname and emulator_first_pathname) else os.path.sep)

            message = r'''
            Please install emulator for {system_name} ({emulator_name}) from <a href="{emulator_url}" style="text-decoration:none;">{emulator_url}</a> to <a href="{emulator_pathname}" style="text-decoration:none;">{emulator_pathname}</a>
            '''.format(
                system_name=emulator.system_name,
                emulator_name=emulator.emulator_name,
                emulator_url=emulator.emulator_url,
                emulator_pathname=emulator_pathname
            ).strip()

            self._show_message(message)
            return

        if not roms:
            roms_base_first_pathname = emulator.roms_search_path[0] if emulator.roms_search_path else ''
            roms_first_pathname = emulator.roms_paths[0] if emulator.roms_paths else ''

            roms_pathname = os.path.realpath(os.path.join(roms_base_first_pathname, roms_first_pathname) if (roms_base_first_pathname and roms_first_pathname) else os.path.sep)
            formats = Utils.lists_to_string(emulator.run_patterns_roms_extensions, ' ').replace('*', '')

            message = r'''
            Please put yout roms for {system_name} ({emulator_name}) to <a href="{roms_pathname}" style="text-decoration:none;">{roms_pathname}</a> in {formats} format.
            '''.format(
                system_name=emulator.system_name,
                emulator_name=emulator.emulator_name,
                roms_pathname=roms_pathname,
                formats=formats
            ).strip()

            self._show_message(message)
            return


    def _adjust_gui(self):
        show_emulator_name = self._config_global_section['show_emulator_name'] == '1'
        show_emulator_roms_count = self._config_global_section['show_emulator_roms_count'] == '1'

        if show_emulator_name or show_emulator_roms_count:
            self._emu_selector.setFont(QtGui.QFont('Terminal', 10))


    def _show_message(self, message:str):
        show = message != ''

        if show:
            self._games_list.hide()
            self._message_label.show()
        else:
            self._games_list.show()
            self._message_label.hide()

        self._message_label.setText(message)


    def _format_emulator_name(self, iemulator:Emulator) -> str:
        show_emulator_name = self._config_global_section['show_emulator_name'] == '1'
        show_emulator_roms_count = self._config_global_section['show_emulator_roms_count'] == '1'
        fix_game_title = self._config_global_section['fix_game_title'] == '1'

        if show_emulator_name or show_emulator_roms_count:
            formatted_name = '{system_name:<50}'.format(system_name=iemulator.system_name)

            if show_emulator_name:
                formatted_name += '{emulator_name:<10}'.format(emulator_name=iemulator.emulator_name)

            if show_emulator_roms_count:
                formatted_name += '{roms_count}'.format(roms_count = len(iemulator.get_emulator_roms(fixup_titles=fix_game_title)))
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
        self._show_warning_message()


    def _parse_emulator_config(self, emulator_config_section_name:str, emulator_config_section_data:dict):
        run_patterns = []
        run_patterns_roms_extensions = []
        rom_name_remove = []
        custom_data = {}

        for ikey in emulator_config_section_data:
            if ikey.startswith('run_pattern') and not ikey.endswith('_roms_extensions'):
                roms_extensions = emulator_config_section_data[ikey + '_roms_extensions'].strip()

                run_patterns.append(emulator_config_section_data[ikey].strip())
                run_patterns_roms_extensions.append(
                    Utils.string_split_strip(roms_extensions.lower(), ',')
                )
            elif ikey.startswith('rom_name_remove'):
                regex_value = emulator_config_section_data[ikey]

                if len(regex_value) >= 2 and regex_value[0] == "'" and regex_value[-1] == "'":
                    regex_value = regex_value[1:-1]

                rom_name_remove.append(regex_value)
            elif ikey.startswith('x_'):
                custom_data[ikey] = emulator_config_section_data[ikey]

        return {
            'system_name': emulator_config_section_data['system_name'].strip(),
            'emulator_name': emulator_config_section_data['emulator_name'].strip(),
            'emulator_url': emulator_config_section_data['emulator_url'].strip(),
            'internal_name': emulator_config_section_name.strip(),
            'exe_paths': Utils.string_split_strip(
                emulator_config_section_data['exe_paths'].replace('\\', os.sep),
                ','
            ),
            'roms_paths': Utils.string_split_strip(
                emulator_config_section_data['roms_paths'].replace('\\', os.sep),
                ','
            ),
            'run_patterns': run_patterns,
            'run_patterns_roms_extensions': run_patterns_roms_extensions,
            'rom_name_remove': rom_name_remove,
            'rom_basename_ignore': Utils.string_split_strip(
                emulator_config_section_data['rom_basename_ignore'],
                ','
            ),
            'custom_data': custom_data
        }


    def _prepare_search_paths(self, search_paths:str) -> List[str]:
        search_paths_split = Utils.string_split_strip(search_paths, ',')
        processed_paths = []

        for ipath in search_paths_split:
            expanded_paths = os.path.expandvars(ipath).split(os.path.pathsep)

            for iprocessed_path in expanded_paths:
                if not iprocessed_path:
                    continue

                if iprocessed_path and iprocessed_path[0] == '$':
                    # skip not recognized environment variable
                    continue

                if iprocessed_path not in processed_paths:
                    processed_paths.append(iprocessed_path)

        return processed_paths


    def _load_emulators(self) -> list:
        show_non_roms_emulator = self._config_global_section['show_non_roms_emulator'] == '1'
        show_non_exe_emulator = self._config_global_section['show_non_exe_emulator'] == '1'
        sort_emulators = self._config_global_section['sort_emulators'] == '1'
        fix_game_title = self._config_global_section['fix_game_title'] == '1'

        emulators = []

        for isection_name in self._config.sections():
            if not isection_name.startswith('emulator.'):
                continue

            isection_data = dict(self._config[isection_name].items())
            emulator_config = self._parse_emulator_config(isection_name, isection_data)

            emulator_config['systems_search_path'] = self._systems_search_path
            emulator_config['roms_search_path'] = self._roms_search_path
            emulator_config['bios_search_path'] = self._bios_search_path

            iemulator = Emulator(**emulator_config)

            if not show_non_exe_emulator:
                # check if emulator executable exists
                if not iemulator.get_emulator_executable():
                    continue

            if not show_non_roms_emulator:
                # check if emulator have roms
                if not iemulator.get_emulator_roms(fixup_titles=fix_game_title):
                    continue

            emulators.append(iemulator)

        if sort_emulators:
            emulators = sorted(emulators, key=operator.attrgetter('system_name'))

        return emulators


    def _message_box(self, text: str, error:bool = False):
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
            self._log_exception(x)
            exit(1)


    def _get_current_emulator(self) -> Optional[Emulator]:
        current_index = self._emu_selector.currentIndex()

        if current_index <= -1:
            return None

        return self._emulators[current_index]


    def _show_current_emulator_roms(self, first_run:bool = False, cached:bool = True):
        fix_game_title = self._config_global_section['fix_game_title'] == '1'

        try:
            self._games_list.clear()

            emulator = self._get_current_emulator()

            if not emulator:
                return

            self._roms = self._get_current_emulator().get_emulator_roms(cached, fixup_titles=fix_game_title)

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
            self._log_exception(x)


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

        self._message_box(str(x), True)


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
        self._show_warning_message()


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

        self._message_box(msg)


    def _config_button_clicked(self):
        target_config_pathname = os.path.join(os.getcwd(), DEFAULT_CONFIG_PATHNAME)

        if not os.path.exists(DEFAULT_CONFIG_PATHNAME):
            try:
                Utils.file_write_lines(
                    DEFAULT_CONFIG_PATHNAME,
                    DEFAULT_CONFIG.strip().splitlines(False)
                )

                self._message_box('Configuration file written to ' + target_config_pathname)
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
