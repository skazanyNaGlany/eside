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
import patoolib

import warnings
warnings.simplefilter('ignore', UserWarning)

from typeguard import typechecked
from typing import Optional, List

from PySide2.QtWidgets import (                 # pylint: disable=no-name-in-module
    QApplication,
    QDialog,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QLabel,
    QComboBox,
    QMessageBox,
    QListWidgetItem,
    QSizePolicy,
    QMenu,
    QAction
)
from PySide2 import QtCore, QtGui
from PySide2.QtCore import Qt, QTimer                           # pylint: disable=no-name-in-module
from PySide2.QtGui import QKeyEvent, QFont, QGuiApplication     # pylint: disable=no-name-in-module

from configparser import ConfigParser


if __name__ != '__main__':
    print('Do not import this file, just run.')
    exit(1)

if sys.version_info[0] < 3 or sys.version_info[1] < 5:
    print('Python 3.5+ is required.')
    exit(2)


APP_NAME = 'ESide v0.1'
APP_ICON = 'iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAgAElEQVR4Xu3dT8xm533W8fu8M5lESKUIWkcF2gUgRP60my5izyKeVcKqUtWME2CD2DRsqFhUorEpDyV2kbpAZUO6QWyAxE5VqSuSBXKysJ1FNyVxEIIuWqCKSxGlC5LJzHvQ2KlIWtLHfd7rd+5z7vtjKVIW51y/+/5ev/POd2asZGn+QQABBBBAAIHpCCzT3diFEUAAAQQQQKARAEuAAAIIIIDAhAQIwISluzICCCCAAAIEwA4ggAACCCAwIQECMGHprowAAggggAABsAMIIIAAAghMSIAATFi6KyOAAAIIIEAA7AACCCCAAAITEiAAE5buyggggAACCBAAO4AAAggggMCEBAjAhKW7MgIIIIAAAgTADiCAAAIIIDAhAQIwYemujAACCCCAAAGwAwgggAACCExIgABMWLorI4AAAgggQADsAAIIIIAAAhMSIAATlu7KCCCAAAIIEAA7gAACCCCAwIQECMCEpbsyAggggAACBMAOIIAAAgggMCEBAjBh6a6MAAIIIIAAAbADCCCAAAIITEiAAExYuisjgAACCCBAAOwAAggggAACExIgABOW7soIIIAAAggQADuAAAIIIIDAhAQIwISlz3Tl+z/6T7/3G7cfvWvrO//ql559o7W2bj130HnLj33g+Se2vts7H976+ku/9g9+b+u55iGwFQECsBVpc7oQuH/3haeur9cnl9b+9BYHWJZlXddHX3z/a4++eGqn6y1mjj7j1E5XX37y1geX5dYH13Xd5GfW2tr/Xpb1S5999blXRufrfvMS2ORjmhevm/cm8BNPPv/M1XL1XGvrD290loePrr/5oR/50voFApAh/lgAfv0Dy9O3rt7x+dba7Uzq2ZQvX6/rP/nl15598eyTHkDgoAQIwEGLc+y3R4AAvD1Oe36KAOy5HWc7MgECcOT2nP0sAQJwFtHuHyAAu6/IAQ9KgAActDjHfnsE3hKA5R+21t7/9t648VP+CuDGCL8zgACEgYpD4FsECIBVGJoAATh+vQTg+B26wT4JEIB99uJUIQIEIASyYwwB6Ajf6KEJEICh63U5/w7A8XeAABy/QzfYJwECsM9enCpEgACEQHaMIQAd4Rs9NAECMHS9LkcAjr8DBOD4HbrBPgkQgH324lQhAgQgBLJj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'
APP_URL = 'https://github.com/skazanyNaGlany/eside'
DEFAULT_CONFIG_PATHNAME = 'eside.ini'
ANTIMICRO_PROFILE_EXTENSION = '.gamecontroller.amgp'
ANTIMICRO_EXECUTABLES = ['antimicro.exe', 'antimicro']
DEFAULT_CONFIG = r"""
[global]
# ESide default configuration file. You can create your configuration
# by using Configuration option, it will create eside.ini file
# which you can edit to make your own changes.
#
# 1 enable, 0 disable
minimum_window_width = 640
minimum_window_height = 500
start_maximized = 0
systems_base_path = systems
roms_base_path = roms
covers_base_path = roms/covers
bios_path = systems/bios
themes_base_path = themes
theme = default

# show emulator even if it has no roms
show_non_roms_emulator = 1

# show emulator even if it has no executable (not found in systems/ directory)
show_non_exe_emulator = 1

# show emulator name next to system name (eg. Sony PlayStation2 (PCSX2))
show_emulator_name = 0

# show count of roms next to system name (eg. Sony PlayStation 2 [60])
show_emulator_roms_count = 0

# set to 0 to show only "Run selected game" and "Antimicro profile" buttons
show_other_buttons = 1

# show games covers, you must put your covers to roms/covers/<system> and name it like rom name
# eg. "roms/covers/amiga/Brian the Lion (1994)(Psygnosis)(AGA)(M4)[cr Comax](Disk 1 of 3).adf.jpeg"
# png, jpg, jpeg extensions are supported
show_covers = 1

sort_emulators = 1
default_emulator = emulator.fs-uae

# some roms has weird names, eg. Smurfs, The (Europe) (En,Fr,De,Es).gb
# that option will fix it before show in games list
# The Smurfs (Europe) (En,Fr,De,Es).gb
fix_game_title = 1

# cut title to first underscore (if no spaces)
fix_game_title2 = 1

# split title by other case and numbers (eg. CannonFodder2 -> Cannon Fodder 2)
fix_game_title3 = 1

# if your covers are in different size, that option will adjust all covers sizes to
# the same as first cover is
covers_same_size = 1

# "antimicro is a graphical program used to map keyboard keys and mouse controls to a gamepad.
# This program is useful for playing PC games using a gamepad that do not have any form of built-in gamepad support"
#
# you can create your own AntiMicro profiles for your gamepad, and put it to systems/antimicro/profiles
# each profile must be named:
# <section emulator name>.<your own profile name>.gamecontroller.amgp
#
# for example:
# emulator.project64.xbox_one.p1.gamecontroller.amgp
#
# ESide will load all AntiMicro profiles when you switch emulator
# and you can change the profile by clicking on AntiMicro profile button
#
# ESide will start AntiMicro with desired profile just before the game
# and terminate it when you exit the game
#
# I'm using it to play Doom 64 for Nintendo 64 and Final Doom for Sony PlayStation
antimicro_path = systems/antimicro
antimicro_profiles_path = systems/antimicro/profiles

# supported emulators and systems
# you must put desired emulator to systems/ eg. systems/epsxe/
# and configur it before use in ESide (set controllers, bios)

[emulator.epsxe]
system_name = Sony PlayStation
emulator_name = ePSXe
emulator_url = https://www.epsxe.com/
exe_paths = epsxe/ePSXe.exe, epsxe/epsxe_x64
gui_paths =
roms_path = psx
rom_basename_ignore =
run_pattern0 = "{exe_path}" -loadbin "{rom_path}" -nogui
run_pattern0_roms_extensions = *.cue, *.ccd, *.img, *.iso, *.bin
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.pcsx2]
system_name = Sony PlayStation 2
emulator_name = PCSX2
emulator_url = https://pcsx2.net/
exe_paths = pcsx2/pcsx2.exe, pcsx2/PCSX2
gui_paths =
roms_path = ps2
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
exe_paths = ppsspp/PPSSPPWindows.exe, ppsspp/PPSSPPSDL
gui_paths =
roms_path = psp
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
exe_paths = dolphin/Dolphin.exe, dolphin-emu
gui_paths =
roms_path = gc
rom_basename_ignore =
run_pattern0 = "{exe_path}" -b -e "{rom_path}"
run_pattern0_roms_extensions = *.iso
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.dolphin2]
system_name = Nintendo Wii
emulator_name = Dolphin
emulator_url = https://dolphin-emu.org/
exe_paths = dolphin/Dolphin.exe, dolphin-emu
gui_paths =
roms_path = wii
rom_basename_ignore =
run_pattern0 = "{exe_path}" -b -e "{rom_path}"
run_pattern0_roms_extensions = *.iso
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.cemu]
system_name = Nintendo Wii U
emulator_name = Cemu
emulator_url = https://cemu.info/
exe_paths = cemu/Cemu.exe
gui_paths =
roms_path = wiiu
rom_basename_ignore =
run_pattern0 = "{exe_path}" -f -g "{rom_path}"
run_pattern0_roms_extensions = *.wud, *.wux, *.iso, *.wad, *.rpx
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.redream]
system_name = Sega Dreamcast
emulator_name = Redream
emulator_url = https://redream.io/
exe_paths = redream/redream.exe, redream/redream
gui_paths =
roms_path = dreamcast
rom_basename_ignore =
run_pattern0 = "{exe_path}" "{rom_path}"
run_pattern0_roms_extensions = *.cdi, *.chd, *.gdi
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.xenia]
system_name = Microsoft XBox 360
emulator_name = Xenia
emulator_url = https://xenia.jp/
exe_paths = xenia/xenia.exe
gui_paths =
roms_path = x360
rom_basename_ignore = *.log
run_pattern0 = "{exe_path}" "{rom_path}" --fullscreen
run_pattern0_roms_extensions = *.iso, *.xex, *.xcp, *
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.vba-m]
system_name = Nintendo Game Boy
emulator_name = VisualBoyAdvance-M
emulator_url = https://vba-m.com/
exe_paths = vba-m/visualboyadvance-m.exe
gui_paths =
roms_path = gb
rom_basename_ignore =
run_pattern0 = "{exe_path}" /f "{rom_path}"
run_pattern0_roms_extensions = *.gb
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.vba-m2]
system_name = Nintendo Game Boy Color
emulator_name = VisualBoyAdvance-M
emulator_url = https://vba-m.com/
exe_paths = vba-m/visualboyadvance-m.exe
gui_paths =
roms_path = gbc
rom_basename_ignore =
run_pattern0 = "{exe_path}" /f "{rom_path}"
run_pattern0_roms_extensions = *.gb, *.gbc
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.vba-m3]
system_name = Nintendo Game Boy Advance
emulator_name = VisualBoyAdvance-M
emulator_url = https://vba-m.com/
exe_paths = vba-m/visualboyadvance-m.exe
gui_paths =
roms_path = gba
rom_basename_ignore =
run_pattern0 = "{exe_path}" /f "{rom_path}"
run_pattern0_roms_extensions = *.gba
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.mame]
system_name = Arcade
emulator_name = MAME
emulator_url = https://www.mamedev.org/
exe_paths = mame/mame64.exe, mame
gui_paths =
roms_path = arcade
rom_basename_ignore =
run_pattern0 = "{exe_path}" -rompath "{roms_path}" "{rom_path}"
run_pattern0_roms_extensions = *.zip
rom_name_remove0 =
rom_name_remove1 =

[emulator.fceux]
system_name = Nintendo Entertainment System
emulator_name = FCEUX
emulator_url = http://fceux.com/web/home.html
exe_paths = fceux/fceux.exe
gui_paths =
roms_path = nes
rom_basename_ignore =
run_pattern0 = "{exe_path}" "{rom_path}"
run_pattern0_roms_extensions = *.nes
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.snes9x]
system_name = Super Nintendo Entertainment System
emulator_name = SNES9X
emulator_url = http://www.snes9x.com/
exe_paths = snes9x/snes9x*.exe
gui_paths =
roms_path = snes
rom_basename_ignore =
run_pattern0 = "{exe_path}" -fullscreen "{rom_path}"
run_pattern0_roms_extensions = *.sfc, *.smc
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.project64]
system_name = Nintendo 64
emulator_name = Project64
emulator_url = https://www.pj64-emu.com/
exe_paths = project64/Project64.exe
gui_paths =
roms_path = n64
rom_basename_ignore =
run_pattern0 = "{exe_path}" "{rom_path}"
run_pattern0_roms_extensions = *.n64
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.desmume]
system_name = Nintendo DS
emulator_name = DeSmuME
emulator_url = http://desmume.org/
exe_paths = desmume/DeSmuME*.exe
gui_paths =
roms_path = nds
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
exe_paths = citra/nightly-mingw/citra-qt.exe
gui_paths =
roms_path = 3ds
rom_basename_ignore =
run_pattern0 = "{exe_path}" "{rom_path}"
run_pattern0_roms_extensions = *.3ds
rom_name_remove0 = \[[^\]]*\]
rom_name_remove1 = \(.*\)

[emulator.fs-uae]
system_name = Commodore Amiga
emulator_name = FS-UAE
emulator_url = https://fs-uae.net/
exe_paths = fs-uae/System/FS-UAE/Windows/x86-64/fs-uae.exe, fs-uae/Windows/x86-64/fs-uae.exe, fs-uae/System/FS-UAE/Linux/x86-64/fs-uae, fs-uae/FS-UAE/Linux/x86-64/fs-uae
gui_paths = fs-uae/Launcher.exe, fs-uae/Launcher
roms_path = amiga
rom_basename_ignore =
x_floppy_drive_speed = 0
x_amiga_model = a1200
x_whdload_path = systems/whdload/WHDLoad
x_whdload_args = PRELOAD NOVBRMOVE NOWRITECACHE
run_pattern0 = \"{exe_path}\" --amiga-model={x_amiga_model} {{iterate_roms:--floppy-drive-{rom_index}=\"{rom_path}\":4}} {{iterate_all_roms:--floppy-image-{rom_index}=\"{rom_path}\":20}} --fullscreen --stretch=1 --zoom=auto --smoothing=1 --kickstart_dir=\"{bios_path}\" --floppy_drive_speed={x_floppy_drive_speed}
run_pattern0_roms_extensions = *.adf
run_pattern1 = "{exe_path}" --amiga-model={x_amiga_model} --fullscreen --stretch=1 --zoom=auto --smoothing=1 --kickstart_dir="{bios_path}" --chip_memory=8192 --hard-drive-0="{x_whdload_path}" --hard-drive-1="{unpacked_rom_path-first_directory}"
run_pattern1_roms_extensions = *.lha, *.zip
run_pattern1_precmd_0 = copy {bios_path}/amiga-os-*.rom {x_whdload_path}/Devs/Kickstarts/
run_pattern1_precmd_1 = copy {bios_path}/kick*.A* {x_whdload_path}/Devs/Kickstarts/
run_pattern1_precmd_2 = unpack {rom_path}
run_pattern1_precmd_3 = delete {x_whdload_path}/S/Startup-Sequence
run_pattern1_precmd_4 = write {x_whdload_path}/S/Startup-Sequence CD DH1:
run_pattern1_precmd_5 = write_basename {unpacked_rom_path}/**/*.Slave {x_whdload_path}/S/Startup-Sequence C:WHDLoad SLAVE={write_basename} {x_whdload_args}
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


    @staticmethod
    def adjust_to_system_path(path:str) -> str:
        return os.path.realpath(os.path.normpath(path))


    @staticmethod
    def adjust_dict_all_to_system_path(dict_keys:dict) -> dict:
        for ikey in dict_keys:
            if os.path.exists(dict_keys[ikey]):
                dict_keys[ikey] = Utils.adjust_to_system_path(dict_keys[ikey])

        return dict_keys


    @staticmethod
    def join_paths(*paths) -> str:
        joined = os.path.join(*paths)

        return Utils.adjust_to_system_path(joined)


    @staticmethod
    def find_file_from_list(files_list:list) -> Optional[str]:
        for ifile in files_list:
            if os.path.exists(ifile) and os.path.isfile(ifile):
                return ifile

        return None


    @staticmethod
    def find_file(pattern:str) -> Optional[str]:
        exists = glob.glob(pattern, recursive=True)

        if len(exists):
            return exists[0]

        return None


    @staticmethod
    def copy_files(src_files:list, dst:str, target_is_directory:bool, overwrite:Optional[bool] = False):
        if target_is_directory:
            os.makedirs(dst, exist_ok=True)

        for ifile in src_files:
            with open(ifile, 'rb') as sf:
                if target_is_directory:
                    # copy to directory
                    target_pathname = os.path.join(dst, os.path.basename(ifile))

                    if not overwrite and os.path.exists(target_pathname):
                        continue

                    with open(target_pathname, 'wb') as df:
                        shutil.copyfileobj(sf, df)
                else:
                    with open(dst, 'wb') as df:
                        shutil.copyfileobj(sf, df)


    @staticmethod
    def find_first_directory(root_directory:str) -> Optional[str]:
        for ientry in os.listdir(root_directory):
            full_pathname = os.path.join(root_directory, ientry)

            if os.path.isdir(full_pathname):
                return full_pathname

        return None


@typechecked_class_decorator()
class Emulator:
    re_cue_bin_sign = re.compile(r'^FILE\ \"(.*)\"\ BINARY$')
    re_similar_rom_sign = re.compile(r'\(Disk\ \d\ of\ \d\)')


    def __init__(self,
        system_name: str,
        emulator_name: str,
        emulator_url: str,
        exe_paths: List[str],
        gui_paths: List[str],
        raw_exe_paths: List[str],
        run_patterns: List[str],
        roms_path: str,
        raw_roms_path: str,
        run_patterns_roms_extensions: List[List[str]],
        run_patterns_pre_commands: List[List],
        rom_name_remove: List[str],
        internal_name: str,
        rom_basename_ignore: List[str],
        # globals:
        bios_path: str,
        custom_data: dict
    ):
        self.system_name = system_name
        self.emulator_name = emulator_name
        self.emulator_url = emulator_url
        self.exe_paths = exe_paths
        self.gui_paths = gui_paths
        self.raw_exe_paths = raw_exe_paths
        self.run_patterns = run_patterns
        self.roms_path = roms_path
        self.raw_roms_path = raw_roms_path
        self.rom_name_remove = rom_name_remove
        self.run_patterns_roms_extensions = run_patterns_roms_extensions
        self.run_patterns_pre_commands = run_patterns_pre_commands
        self.internal_name = internal_name
        self.rom_basename_ignore = rom_basename_ignore
        self.bios_path = bios_path
        self.custom_data = custom_data
        self._cached_roms = None
        self._cached_exe_pathname = None
        self._cached_gui_exe_pathname = None
        self._cached_roms_pathname = None
        self._cached_bios_pathname = None

        self._roms_config = self._parse_roms_config()


    def get_full_roms_path(self) -> Optional[str]:
        if not os.path.exists(self.roms_path):
            return None

        return os.path.realpath(self.roms_path)


    def _get_cue_bins(self, cue_pathname: str) -> list:
        bins = []

        for iline in Utils.file_extract_lines(cue_pathname):
            iline = iline.strip()

            match = Emulator.re_cue_bin_sign.findall(iline)

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

        for ipath2 in self.exe_paths:
            ipath2_full_pathname = ipath2

            exists = glob.glob(ipath2_full_pathname)

            if len(exists) and os.path.isfile(exists[0]):
                exe_pathname = os.path.realpath(exists[0])
                break

            ipath2_basename = os.path.basename(ipath2)

            ipath2_basename_system = shutil.which(ipath2_basename)

            if ipath2_basename_system:
                exe_pathname = ipath2_basename_system
                break

            ipath2_full_pathname = ipath2_basename

            exists = glob.glob(ipath2_full_pathname)

            if len(exists) and os.path.isfile(exists[0]):
                exe_pathname = os.path.realpath(exists[0])
                break

        self._cached_exe_pathname = exe_pathname

        return exe_pathname


    def _get_gui_executable(self, cached: bool = True) -> Optional[str]:
        if cached and self._cached_gui_exe_pathname is not None:
            return self._cached_gui_exe_pathname

        exe_pathname = None

        for ipath2 in self.gui_paths:
            ipath2_full_pathname = ipath2

            exists = glob.glob(ipath2_full_pathname)

            if len(exists) and os.path.isfile(exists[0]):
                exe_pathname = os.path.realpath(exists[0])
                break

            ipath2_basename = os.path.basename(ipath2)

            ipath2_basename_system = shutil.which(ipath2_basename)

            if ipath2_basename_system:
                exe_pathname = ipath2_basename_system
                break

            ipath2_full_pathname = ipath2_basename

            exists = glob.glob(ipath2_full_pathname)

            if len(exists) and os.path.isfile(exists[0]):
                exe_pathname = os.path.realpath(exists[0])
                break

        self._cached_gui_exe_pathname = exe_pathname

        return exe_pathname


    def get_gui_executable(self, cached: bool = True) -> Optional[str]:
        exe_pathname = self._get_gui_executable(cached)

        if exe_pathname:
            return exe_pathname

        return self.get_emulator_executable(cached)


    def _ignore_file(self, filename:str) -> bool:
        for ipattern in self.rom_basename_ignore:
            if fnmatch.fnmatch(filename, ipattern):
                return True

        return False


    def _parse_roms_config(self) -> Optional[ConfigParser]:
        roms_path = self.get_full_roms_path()

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
        roms_path = self.get_full_roms_path()
        roms = {}
        to_skip = []

        if not roms_path or not os.path.exists(roms_path):
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

                if rom_config and 'hide' in rom_config and rom_config['hide'] == '1':
                    continue

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


    def _fixup_game_titles2(self, roms:dict) -> dict:
        for pathname in roms.copy():
            name = roms[pathname]

            if name.count(' ') > 0 or not name.count('_'):
                continue

            parts = name.split('_', 1)

            if len(parts) >= 1:
                roms[pathname] = parts[0]

        return roms


    def _fixup_game_titles3(self, roms:dict) -> dict:
        for pathname in roms.copy():
            name = roms[pathname]

            if name.count(' ') > 0:
                continue

            parts = [p.strip() for p in re.split(r'([A-Z][a-z]*)', name) if p.strip() != '']
            name = ' '.join(parts)

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


    def get_emulator_roms(self,
                          cached:bool = True,
                          fixup_titles:bool = False,
                          fixup_titles2:bool = False,
                          fixup_titles3:bool = False
    ) -> Optional[dict]:
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

        if fixup_titles2:
            roms = self._fixup_game_titles2(roms)

        if fixup_titles3:
            roms = self._fixup_game_titles3(roms)

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


    def _find_rom_run_pattern_index(self, rom_path:str) -> Optional[int]:
        rom_path_basename = os.path.basename(rom_path.lower())

        for irun_pattern_roms_extensions in self.run_patterns_roms_extensions:
            for iextension in irun_pattern_roms_extensions:
                if fnmatch.fnmatch(rom_path_basename, iextension):
                    run_pattern_index = self.run_patterns_roms_extensions.index(irun_pattern_roms_extensions)

                    return run_pattern_index

        return None


    def _find_similar_roms(self, rom_path:str) -> List[str]:
        dirname = os.path.dirname(rom_path)
        basename = os.path.basename(rom_path)

        (filename, extension) = os.path.splitext(basename)

        match = Emulator.re_similar_rom_sign.findall(basename)
        len_match = len(match)

        if len_match != 1:
            return [rom_path]

        (no_disc_filename, count) = Emulator.re_similar_rom_sign.subn('', basename, 1)
        (clean_filename, extension) = os.path.splitext(no_disc_filename)

        files = glob.glob(os.path.join(dirname, '*' + extension))
        similar = []

        for ifile in files:
            ifile_basename = os.path.basename(ifile)

            if ifile_basename.startswith(clean_filename) and len(Emulator.re_similar_rom_sign.findall(ifile_basename)) == 1 and ifile_basename.endswith(extension):
                if ifile not in similar:
                    similar.append(ifile)

        return sorted(similar)


    def _process_extended_pattern(self, pattern:str, rom_path:str, run_pattern_data:dict) -> str:
        if '{unpacked_rom_path-first_directory}' in pattern and 'unpacked_rom_path' in run_pattern_data:
            run_pattern_data['unpacked_rom_path-first_directory'] = Utils.find_first_directory(run_pattern_data['unpacked_rom_path'])

            return pattern

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


    def _run_pre_commands(self, pre_commands:list, run_pattern_data:dict):
        if not self.run_patterns_pre_commands:
            return

        for icmd in pre_commands:
            if icmd.startswith('copy '):
                icmd_parts = icmd.split(' ', 3)

                if len(icmd_parts) < 3:
                    continue

                target_is_directory = icmd_parts[2].endswith('\\') or icmd_parts[2].endswith('/')

                icmd_parts[1] = Utils.adjust_to_system_path(icmd_parts[1].format(**run_pattern_data))
                icmd_parts[2] = Utils.adjust_to_system_path(icmd_parts[2].format(**run_pattern_data))

                Utils.copy_files(glob.glob(icmd_parts[1]), icmd_parts[2], target_is_directory)
            elif icmd.startswith('unpack '):
                icmd_parts = icmd.split(' ', 2)

                if len(icmd_parts) < 2:
                    continue

                icmd_parts[1] = Utils.adjust_to_system_path(icmd_parts[1].format(**run_pattern_data))

                (root, ext) = os.path.splitext(os.path.basename(icmd_parts[1]))

                unpacked_rom_path = os.path.join(run_pattern_data['roms_path'], root)
                run_pattern_data['unpacked_rom_path'] = unpacked_rom_path

                if os.path.exists(unpacked_rom_path):
                    continue

                os.makedirs(unpacked_rom_path, exist_ok=True)

                try:
                    patoolib.extract_archive(icmd_parts[1], outdir=unpacked_rom_path, interactive=False)
                except Exception as x:
                    x_str = str(x)

                    if ' returned non-zero exit status ' in x_str:
                        # omit error when archive cannot be unpacked
                        # but log it to the standard output
                        print(x_str)
                    else:
                        raise x
            elif icmd.startswith('delete '):
                icmd_parts = icmd.split(' ', 2)

                if len(icmd_parts) < 2:
                    continue

                icmd_parts[1] = Utils.adjust_to_system_path(icmd_parts[1].format(**run_pattern_data))

                if os.path.exists(icmd_parts[1]):
                    os.remove(icmd_parts[1])
            elif icmd.startswith('write '):
                icmd_parts = icmd.split(' ', 2)

                if len(icmd_parts) < 2:
                    continue

                icmd_parts[1] = Utils.adjust_to_system_path(icmd_parts[1].format(**run_pattern_data))
                icmd_parts[2] = icmd_parts[2].format(**run_pattern_data)

                with open(icmd_parts[1], 'a+', newline='') as f:
                    print(icmd_parts[2], sep='\r', file=f)
            elif icmd.startswith('write_basename '):
                icmd_parts = icmd.split(' ', 3)

                if len(icmd_parts) < 3:
                    continue

                icmd_parts[1] = Utils.adjust_to_system_path(icmd_parts[1].format(**run_pattern_data))
                icmd_parts[2] = Utils.adjust_to_system_path(icmd_parts[2].format(**run_pattern_data))

                run_pattern_data['write_basename'] = os.path.basename(str(Utils.find_file(icmd_parts[1])))

                icmd_parts[3] = icmd_parts[3].format(**run_pattern_data)

                with open(icmd_parts[2], 'a+', newline='') as f:
                    print(icmd_parts[3], sep='\r', file=f)


    def run_rom(self, rom_path: str) -> subprocess:
        exe_path = self.get_emulator_executable()

        if not exe_path:
            self._raise_no_exe_exception()

        run_pattern_index = self._find_rom_run_pattern_index(rom_path)

        if run_pattern_index is None:
            # should not get here
            self._raise_no_rom_run_pattern_exception(rom_path)

        run_pattern = self.run_patterns[run_pattern_index]

        run_pattern_data = {
            'exe_path': exe_path,
            'rom_path': rom_path,
            'roms_path': self.get_full_roms_path(),
            'bios_path': self.bios_path
        }

        if self.custom_data:
            run_pattern_data.update(self.custom_data)

        if self.run_patterns_pre_commands and run_pattern_index < len(self.run_patterns_pre_commands):
            self._run_pre_commands(self.run_patterns_pre_commands[run_pattern_index], run_pattern_data)

        rom_config = self._find_rom_config(os.path.basename(rom_path))

        if rom_config:
            run_pattern_data.update(rom_config)

        run_pattern = self._process_extended_pattern(run_pattern, rom_path, run_pattern_data)

        run_pattern_data = Utils.adjust_dict_all_to_system_path(run_pattern_data)

        run_command = run_pattern.format(**run_pattern_data)
        print('Running command: ' + run_command)

        args = shlex.split(run_command)

        self._running_rom = subprocess.Popen(args, cwd=os.path.dirname(exe_path))

        return self._running_rom


    def run_gui(self) -> subprocess:
        exe_path = self.get_gui_executable()

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

        self._re_run_pattern = re.compile(r'^run_pattern\d+$')
        self._re_run_pattern_roms_extensions = re.compile(r'^run_pattern\d+_roms_extensions$')
        self._re_run_pattern_precmd = re.compile(r'^run_pattern\d+_precmd_\d+$')
        self._re_rom_name_remove = re.compile(r'^rom_name_remove\d+$')
        self._re_custom_data = re.compile(r'^x_.*$')

        self._config = self._parse_config()
        self._config_global_section = dict(self._config['global'].items())

        minimum_window_width = int(self._config_global_section['minimum_window_width'])
        minimum_window_height = int(self._config_global_section['minimum_window_height'])
        show_other_buttons = self._config_global_section['show_other_buttons'] == '1'
        self._show_covers = self._config_global_section['show_covers'] == '1'

        self._antimicro_path = Utils.adjust_to_system_path(self._config_global_section['antimicro_path'])
        self._antimicro_profiles_path = Utils.adjust_to_system_path(self._config_global_section['antimicro_profiles_path'])

        self._need_update_cover = True
        self._best_scales = {}
        self._antimicro_profiles = []
        self._selected_antimicro_profile = None
        self._antimicro_process = None
        self._emulator_process = None

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(minimum_window_width, minimum_window_height)
        self.setWindowIcon(self._icon_from_base64(APP_ICON))
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        self._main_layout = QVBoxLayout(self)
        self._horizon_layout = QHBoxLayout()
        self._emu_selector = QComboBox()
        self._games_list = QListWidget()
        self._message_label = QLabel()
        self._run_game_button = QPushButton('Run selected game')
        self._cover_label = None

        if self._show_covers:
            self._cover_label = QLabel()

        self._antimicro_profile_button = None

        if os.path.exists(self._antimicro_profiles_path) and os.path.exists(self._antimicro_profiles_path):
            self._antimicro_profile_button = QPushButton('AntiMicro profile: None')

        if show_other_buttons:
            self._run_emulator_gui_button = QPushButton('Run emulator GUI')
            self._refresh_list_button = QPushButton('Refresh list')
            self._config_button = QPushButton('Configuration')
            self._about_button = QPushButton('About')
            self._exit_button = QPushButton('Exit')

        self._clipboard = QGuiApplication.clipboard()

        self._message_label.setStyleSheet('background-color: transparent; border: 1px ridge gray; padding: 15px;')
        self._message_label.setOpenExternalLinks(True)
        self._message_label.setWordWrap(True)
        self._message_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self._message_label.setFont(QFont('Arial', 11))

        self._main_layout.addWidget(self._emu_selector)
        self._main_layout.addLayout(self._horizon_layout)

        self._horizon_layout.addWidget(self._games_list, 55)

        if self._show_covers:
            self._horizon_layout.addWidget(self._cover_label, 45)

        self._emu_selector.setContentsMargins(0, 0, 0, 10)
        self._horizon_layout.setContentsMargins(0, 0, 0, 10)

        if self._show_covers:
            self._cover_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self._cover_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self._games_list.setUniformItemSizes(True)
        self._games_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._games_list.customContextMenuRequested[QtCore.QPoint].connect(self._games_list_right_menu)

        self._main_layout.addWidget(self._message_label)

        self._main_layout.addWidget(self._run_game_button)

        if self._antimicro_profile_button:
            self._main_layout.addWidget(self._antimicro_profile_button)

        if show_other_buttons:
            self._main_layout.addWidget(self._run_emulator_gui_button)
            self._main_layout.addWidget(self._refresh_list_button)
            self._main_layout.addWidget(self._config_button)
            self._main_layout.addWidget(self._about_button)
            self._main_layout.addWidget(self._exit_button)

        self._systems_base_path = self._config_global_section['systems_base_path']
        self._roms_base_path = self._config_global_section['roms_base_path']
        self._covers_base_realpath = Utils.adjust_to_system_path(self._config_global_section['covers_base_path'])
        self._themes_base_realpath = Utils.adjust_to_system_path(self._config_global_section['themes_base_path'])
        self._theme = self._config_global_section['theme']
        self._bios_path = self._config_global_section['bios_path']
        self._emulators = self._load_emulators()

        self._show_emulators()
        self._show_current_emulator_roms(True)

        self._emu_selector.currentIndexChanged.connect(self._emu_selector_current_index_changed)
        self._games_list.doubleClicked.connect(self._games_list_double_clicked)
        self._games_list.currentRowChanged.connect(self._games_list_current_row_changed)

        self._run_game_button.clicked.connect(self._run_game_button_clicked)

        if self._antimicro_profile_button:
            self._antimicro_profile_button.clicked.connect(self._antimicro_profile_button_clicked)

        if show_other_buttons:
            self._run_emulator_gui_button.clicked.connect(self._run_emulator_gui_button_clicked)
            self._about_button.clicked.connect(self._about_button_clicked)
            self._config_button.clicked.connect(self._config_button_clicked)
            self._exit_button.clicked.connect(self._exit_button_clicked)
            self._refresh_list_button.clicked.connect(self._refresh_list_button_clicked)

        app.installEventFilter(self)

        self._adjust_gui()

        if self._show_covers:
            self._cover_timer = QTimer(self)
            self._cover_timer.timeout.connect(self._cover_timer_timeout)
            self._cover_timer.start(10)
        else:
            self._need_update_cover = False

        self._antimicro_timer = QTimer(self)
        self._antimicro_timer.timeout.connect(self._antimicro_timer_timeout)
        self._antimicro_timer.start(500)

        start_maximized = self._config_global_section['start_maximized'] == '1'

        if start_maximized:
            self.showMaximized()

        self._load_theme()


    def _load_theme(self):
        if self._theme == 'default':
            return

        theme_realpath = Utils.adjust_to_system_path(os.path.join(
            self._themes_base_realpath,
            self._theme
        ))

        if not os.path.exists(theme_realpath):
            print('Theme {theme} not found'.format(theme=self._theme))
            return

        app.setStyleSheet(open(theme_realpath, 'r').read())


    def _games_list_right_menu(self):
        right_menu = QMenu(self._games_list)

        copy_game_name_action = QAction('&Copy game name', self, triggered = self._games_list_copy_game_name)
        copy_system_game_name_action = QAction('Copy &system && game name', self, triggered = self._games_list_copy_system_game_name)
        copy_rom_pathname_action = QAction('Copy rom &location', self, triggered = self._games_list_copy_rom_pathname)
        copy_rom_filename_action = QAction('Copy rom &filename', self, triggered = self._games_list_copy_rom_filename)
        google_game = QAction('&Google it', self, triggered = self._games_list_google_game)
        run_game = QAction('&Run', self, triggered = self._run_selected_game)

        right_menu.addAction(copy_game_name_action)
        right_menu.addAction(copy_system_game_name_action)
        right_menu.addAction(copy_rom_pathname_action)
        right_menu.addAction(copy_rom_filename_action)
        right_menu.addAction(google_game)
        right_menu.addAction(run_game)

        right_menu.exec_(QtGui.QCursor.pos())


    def _cover_timer_timeout(self):
        self._show_selected_game_cover()


    def _antimicro_timer_timeout(self):
        if not self._antimicro_process:
            return

        if not self._emulator_process:
            if self._antimicro_process:
                self._antimicro_process.terminate()
                self._antimicro_process = None

            return

        if self._emulator_process.poll() is None:
            # still running
            return

        self._emulator_process = None

        # emulator process terminated
        # terminate antimicro
        self._antimicro_process.terminate()
        self._antimicro_process = None


    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()

            if key == Qt.Key_Left:
                self._switch_emulator(False)

                return True
            elif key == Qt.Key_Right:
                self._switch_emulator(True)

                return True

        return super(MainWindow, self).eventFilter(source, event)


    def resizeEvent(self, event):
        self._best_scales = {}
        self._need_update_cover = True


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
        self._load_antimicro_profiles()
        self._switch_antimicro_profile(1)
        self._show_warning_message()


    def _show_warning_message(self):
        fix_game_title = self._config_global_section['fix_game_title'] == '1'
        fix_game_title2 = self._config_global_section['fix_game_title2'] == '1'
        fix_game_title3 = self._config_global_section['fix_game_title3'] == '1'

        current_index = self._emu_selector.currentIndex()

        if current_index <= -1:
            return None

        emulator = self._emulators[current_index]

        exe_pathname = emulator.get_emulator_executable()
        roms = emulator.get_emulator_roms(
            fixup_titles=fix_game_title,
            fixup_titles2=fix_game_title2,
            fixup_titles3=fix_game_title3
        )

        if exe_pathname and roms:
            self._show_message('')
            return

        if not exe_pathname:
            raw_emulator_pathnames = list(set([
                Utils.join_paths(
                    self._systems_base_path,
                    iexe_path.split(os.path.sep)[0]
                ) for iexe_path in emulator.raw_exe_paths
            ]))

            emulator_pathnames = []
            emulator_pathnames_str = ''

            for ipath in raw_emulator_pathnames:
                emulator_pathnames.append('<a href="{path}" style="text-decoration:none;">{path}</a>'.format(path=ipath))

            emulator_pathnames_str = ' or '.join(emulator_pathnames).strip()

            message = r'''
            Please install emulator for {system_name} ({emulator_name}) from <a href="{emulator_url}" style="text-decoration:none;">{emulator_url}</a> to {emulator_pathnames_str}
            '''.format(
                system_name=emulator.system_name,
                emulator_name=emulator.emulator_name,
                emulator_url=emulator.emulator_url,
                emulator_pathnames_str=emulator_pathnames_str
            ).strip()

            self._show_message(message)
            return

        if not roms:
            formats = Utils.lists_to_string(emulator.run_patterns_roms_extensions, ' ').replace('*', '')

            message = r'''
            Please put yout roms for {system_name} ({emulator_name}) to <a href="{roms_path}" style="text-decoration:none;">{roms_path}</a> in {formats} format.
            '''.format(
                system_name=emulator.system_name,
                emulator_name=emulator.emulator_name,
                roms_path=emulator.roms_path,
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

            if self._show_covers:
                self._cover_label.hide()

            self._message_label.show()
        else:
            self._games_list.show()

            if self._show_covers:
                self._cover_label.show()

            self._message_label.hide()

        self._message_label.setText(message)


    def _format_emulator_name(self, iemulator:Emulator) -> str:
        show_emulator_name = self._config_global_section['show_emulator_name'] == '1'
        show_emulator_roms_count = self._config_global_section['show_emulator_roms_count'] == '1'
        fix_game_title = self._config_global_section['fix_game_title'] == '1'
        fix_game_title2 = self._config_global_section['fix_game_title2'] == '1'
        fix_game_title3 = self._config_global_section['fix_game_title3'] == '1'

        if show_emulator_name or show_emulator_roms_count:
            formatted_name = '{system_name:<50}'.format(system_name=iemulator.system_name)

            if show_emulator_name:
                formatted_name += '{emulator_name:<10}'.format(emulator_name=iemulator.emulator_name)

            if show_emulator_roms_count:
                formatted_name += '{roms_count}'.format(roms_count = len(iemulator.get_emulator_roms(
                    fixup_titles=fix_game_title,
                    fixup_titles2=fix_game_title2,
                    fixup_titles3=fix_game_title3
                )))
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


    def _load_antimicro_profiles(self):
        self._antimicro_profiles = []
        self._selected_antimicro_profile = None

        if not os.path.exists(self._antimicro_path) or not os.path.exists(self._antimicro_profiles_path):
            return

        current_emulator_index = self._emu_selector.currentIndex()

        if current_emulator_index <= -1:
            return None

        emulator = self._emulators[current_emulator_index]
        profiles = sorted(list(pathlib.Path(self._antimicro_profiles_path).rglob('*' + ANTIMICRO_PROFILE_EXTENSION)))

        for iprofile in profiles:
            if not iprofile.name.startswith(emulator.internal_name):
                continue

            self._antimicro_profiles.append(str(iprofile))


    def _format_antimicro_profile_name(self, profile_pathname:str) -> str:
        profile_basename = os.path.basename(profile_pathname)

        profile_basename_parts = profile_basename.split('.', 2)

        if len(profile_basename_parts) < 3:
            return profile_basename.replace(ANTIMICRO_PROFILE_EXTENSION, '')

        return profile_basename_parts[2].replace(ANTIMICRO_PROFILE_EXTENSION, '')


    def _switch_antimicro_profile(self, direction:int):
        if self._antimicro_profile_button:
            self._antimicro_profile_button.setText('AntiMicro profile: None')

        if not direction or not self._antimicro_profile_button:
            self._selected_antimicro_profile = None

            return

        antimicro_profiles_copy = self._antimicro_profiles.copy()
        antimicro_profiles_copy.insert(0, None)

        current_index = 0
        len_antimicro_profiles = len(antimicro_profiles_copy)

        if self._selected_antimicro_profile:
            current_index = self._selected_antimicro_profile

        if direction == -1:
            current_index -= 1

            if current_index < 0:
                current_index = len_antimicro_profiles - 1
        elif direction == 1:
            current_index += 1

            if current_index >= len_antimicro_profiles:
                current_index = 0

        if not antimicro_profiles_copy[current_index]:
            self._antimicro_profile_button.setText('AntiMicro profile: None')
            self._selected_antimicro_profile = None

            return

        self._selected_antimicro_profile = current_index
        self._antimicro_profile_button.setText(
            'AntiMicro profile: ' + self._format_antimicro_profile_name(antimicro_profiles_copy[current_index]))


    def _show_emulators(self):
        default_emulator = self._config_global_section['default_emulator']
        default_emulator_index = -1

        self._emu_selector.clear()

        for iemulator in self._emulators:
            self._emu_selector.addItem(self._format_emulator_name(iemulator))

            if default_emulator and default_emulator_index == -1 and iemulator.internal_name == default_emulator:
                default_emulator_index = self._emulators.index(iemulator)

        if default_emulator_index != -1:
            self._emu_selector.setCurrentIndex(default_emulator_index)

        self._update_current_emulator_tooltip()
        self._load_antimicro_profiles()
        self._switch_antimicro_profile(1)
        self._show_warning_message()


    def _prepare_emulator_config(self, emulator_config_section_name:str, emulator_config_section_data:dict):
        run_patterns = []
        run_patterns_roms_extensions = []
        run_patterns_pre_commands = []
        rom_name_remove = []
        custom_data = {}

        for ikey in emulator_config_section_data:
            if self._re_run_pattern.match(ikey):
                run_patterns_pre_commands.append([])

                roms_extensions = emulator_config_section_data[ikey + '_roms_extensions']

                run_patterns.append(emulator_config_section_data[ikey])
                run_patterns_roms_extensions.append(
                    Utils.string_split_strip(roms_extensions.lower(), ',')
                )
            elif self._re_rom_name_remove.match(ikey):
                regex_value = emulator_config_section_data[ikey]

                if len(regex_value) >= 2 and regex_value[0] == "'" and regex_value[-1] == "'":
                    regex_value = regex_value[1:-1]

                rom_name_remove.append(regex_value)
            elif self._re_custom_data.match(ikey):
                custom_data[ikey] = emulator_config_section_data[ikey]
            elif self._re_run_pattern_precmd.match(ikey):
                run_patterns_pre_commands[len(run_patterns_pre_commands) - 1].append(emulator_config_section_data[ikey])

        exe_paths = []
        raw_exe_paths = Utils.string_split_strip(emulator_config_section_data['exe_paths'], ',')

        for iexe_path_key, iexe_path in enumerate(raw_exe_paths):
            exe_paths.append(Utils.join_paths(self._systems_base_path, iexe_path))

        gui_paths = []
        raw_gui_paths = Utils.string_split_strip(emulator_config_section_data['gui_paths'], ',')

        for igui_path_key, igui_path in enumerate(raw_gui_paths):
            gui_paths.append(Utils.join_paths(self._systems_base_path, igui_path))

        return {
            'system_name': emulator_config_section_data['system_name'],
            'emulator_name': emulator_config_section_data['emulator_name'],
            'emulator_url': emulator_config_section_data['emulator_url'],
            'internal_name': emulator_config_section_name,
            'exe_paths': exe_paths,
            'gui_paths': gui_paths,
            'raw_exe_paths': raw_exe_paths,
            'roms_path': Utils.join_paths(self._roms_base_path, emulator_config_section_data['roms_path']),
            'raw_roms_path': emulator_config_section_data['roms_path'],
            'bios_path': Utils.adjust_to_system_path(self._bios_path),
            'run_patterns': run_patterns,
            'run_patterns_roms_extensions': run_patterns_roms_extensions,
            'run_patterns_pre_commands': run_patterns_pre_commands,
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
        fix_game_title2 = self._config_global_section['fix_game_title2'] == '1'
        fix_game_title3 = self._config_global_section['fix_game_title3'] == '1'

        emulators = []

        for isection_name in self._config.sections():
            if not isection_name.startswith('emulator.'):
                continue

            isection_data = dict(self._config[isection_name].items())
            emulator_config = self._prepare_emulator_config(isection_name, isection_data)

            iemulator = Emulator(**emulator_config)

            if not show_non_exe_emulator:
                # check if emulator executable exists
                if not iemulator.get_emulator_executable():
                    continue

            if not show_non_roms_emulator:
                # check if emulator have roms
                if not iemulator.get_emulator_roms(
                    fixup_titles=fix_game_title,
                    fixup_titles2=fix_game_title2,
                    fixup_titles3=fix_game_title3
                ):
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
        fix_game_title2 = self._config_global_section['fix_game_title2'] == '1'
        fix_game_title3 = self._config_global_section['fix_game_title3'] == '1'

        try:
            self._games_list.blockSignals(True)
            self._games_list.clear()

            emulator = self._get_current_emulator()

            if not emulator:
                return

            self._roms = self._get_current_emulator().get_emulator_roms(cached,
                fixup_titles=fix_game_title,
                fixup_titles2=fix_game_title2,
                fixup_titles3=fix_game_title3
            )

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
        finally:
            self._games_list.blockSignals(False)


    def _show_selected_game_cover(self):
        if not self._need_update_cover or not self._show_covers:
            return

        if self._cover_label.isHidden():
            self._cover_label.clear()
            self._need_update_cover = False

            return

        try:
            current_index = self._games_list.currentIndex()

            if not current_index:
                self._cover_label.clear()
                self._need_update_cover = False

                return

            current_emulator = self._get_current_emulator()

            if current_emulator:
                rom_path = self._get_rom_by_index(current_index.row())

                if not rom_path:
                    self._cover_label.clear()
                    self._need_update_cover = False

                    return

                cover_label_size = self._cover_label.size()
                rom_basename = os.path.basename(rom_path)

                search_paths = [
                    os.path.join(self._covers_base_realpath, rom_basename + '.png'),
                    os.path.join(self._covers_base_realpath, rom_basename + '.jpg'),
                    os.path.join(self._covers_base_realpath, rom_basename + '.jpeg'),
                    os.path.join(self._covers_base_realpath, current_emulator.raw_roms_path, rom_basename + '.png'),
                    os.path.join(self._covers_base_realpath, current_emulator.raw_roms_path, rom_basename + '.jpg'),
                    os.path.join(self._covers_base_realpath, current_emulator.raw_roms_path, rom_basename + '.jpeg'),
                ]

                cover_file_pathname = Utils.find_file_from_list(search_paths)

                if not cover_file_pathname:
                    self._cover_label.clear()
                    self._need_update_cover = False

                    return

                if current_emulator.internal_name not in self._best_scales:
                    self._best_scales[current_emulator.internal_name] = {}

                emulator_best_scales = self._best_scales[current_emulator.internal_name]

                covers_same_size = self._config_global_section['covers_same_size']
                first_rom_cover_size = None

                if covers_same_size:
                    first_rom_path = self._get_rom_by_index(0)
                    first_rom_basename = os.path.basename(first_rom_path)

                    first_rom_cover_search_paths = [
                        os.path.join(self._covers_base_realpath, first_rom_basename + '.png'),
                        os.path.join(self._covers_base_realpath, first_rom_basename + '.jpg'),
                        os.path.join(self._covers_base_realpath, first_rom_basename + '.jpeg'),
                        os.path.join(self._covers_base_realpath, current_emulator.raw_roms_path, first_rom_basename + '.png'),
                        os.path.join(self._covers_base_realpath, current_emulator.raw_roms_path, first_rom_basename + '.jpg'),
                        os.path.join(self._covers_base_realpath, current_emulator.raw_roms_path, first_rom_basename + '.jpeg'),
                    ]

                    first_rom_cover_pathname = Utils.find_file_from_list(first_rom_cover_search_paths)

                    if first_rom_cover_pathname:
                        if first_rom_cover_pathname in emulator_best_scales:
                            first_rom_cover_size = emulator_best_scales[first_rom_cover_pathname]
                        else:
                            first_rom_cover_size = self._rescale_cover(current_emulator, first_rom_cover_pathname, cover_label_size).size()

                            first_rom_cover_size = (first_rom_cover_size.width(), first_rom_cover_size.height())

                pixmap = self._rescale_cover(current_emulator, cover_file_pathname, cover_label_size, first_rom_cover_size)

                self._cover_label.setPixmap(pixmap)
        except Exception as x:
            self._log_exception(x)

        self._need_update_cover = False


    def _rescale_cover(self, emulator:Emulator, cover_file_pathname:str, cover_label_size:QtCore.QSize, first_rom_cover_size:Optional[tuple] = None) -> QtGui.QPixmap:
        emulator_best_scales = self._best_scales[emulator.internal_name]

        pixmap = QtGui.QPixmap(cover_file_pathname)
        rescaled = False

        if first_rom_cover_size:
            pixmap = pixmap.scaled(first_rom_cover_size[0], first_rom_cover_size[1], mode=QtCore.Qt.SmoothTransformation)

            rescaled = True

        if not rescaled:
            if cover_file_pathname in emulator_best_scales and emulator_best_scales[cover_file_pathname][0] > 0:
                pixmap = pixmap.scaled(emulator_best_scales[cover_file_pathname][0], emulator_best_scales[cover_file_pathname][1], mode=QtCore.Qt.SmoothTransformation)
            else:
                pixmap_size = pixmap.size()
                pixmap_original = pixmap
                new_width = pixmap_size.width()

                while pixmap_size.width() > cover_label_size.width() or pixmap_size.height() > cover_label_size.height():
                    new_width = int(pixmap_size.width() - ((pixmap_size.width() / 100) * 10))

                    pixmap = pixmap_original.scaledToWidth(new_width, mode=QtCore.Qt.SmoothTransformation)
                    pixmap_size = pixmap.size()

                    if pixmap_size.width() == 0:
                        break

                emulator_best_scales[cover_file_pathname] = (int(pixmap_size.width()), int(pixmap_size.height()))

        return pixmap


    def _get_rom_by_index(self, index: int) -> Optional[str]:
        if not self._roms:
            return None

        return list(self._roms.keys())[index]


    def _exit_button_clicked(self):
        self.close()


    def _refresh_list_button_clicked(self):
        self._show_current_emulator_roms(cached=False)
        self._need_update_cover = True


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
                    self._emulator_process = current_emulator.run_rom(rom_full_path)

                    self._run_antimicro()
        except Exception as x:
            self._log_exception(x)


    def _games_list_double_clicked(self):
        self._run_selected_game()


    def _run_antimicro(self):
        if not self._selected_antimicro_profile or self._antimicro_process:
            return

        executables = []

        for iexe_name in ANTIMICRO_EXECUTABLES:
            executables.append(os.path.join(self._antimicro_path, iexe_name))

        exe_path = Utils.find_file_from_list(executables)

        if not exe_path:
            print('AntiMicro executable not found')

            return

        profile_pathname = self._antimicro_profiles[self._selected_antimicro_profile - 1]

        self._antimicro_process = subprocess.Popen([
            exe_path,
            '--tray',
            '--hidden',
            '--profile',
            profile_pathname
        ])


    def _emu_selector_current_index_changed(self, index):
        self._show_current_emulator_roms(True)
        self._update_current_emulator_tooltip()
        self._load_antimicro_profiles()
        self._switch_antimicro_profile(1)
        self._show_warning_message()
        self._need_update_cover = True


    def _games_list_copy_game_name(self):
        current_row = self._games_list.currentItem()

        if not current_row:
            return

        self._clipboard.setText(current_row.text())


    def _get_current_system_n_game_name(self) -> Optional[str]:
        current_emulator = self._get_current_emulator()
        current_row = self._games_list.currentItem()

        if not current_row:
            return None

        return current_emulator.system_name + ' ' + current_row.text()


    def _games_list_copy_system_game_name(self):
        system_game_name = self._get_current_system_n_game_name()

        if not system_game_name:
            return

        self._clipboard.setText(system_game_name)


    def _get_current_selected_rom(self) -> Optional[str]:
        current_index = self._games_list.currentIndex()

        if not current_index:
            return None

        current_emulator = self._get_current_emulator()

        if not current_emulator:
            return None

        rom_path = self._get_rom_by_index(current_index.row())

        if not rom_path:
            return None

        return os.path.abspath(rom_path)


    def _games_list_copy_rom_pathname(self):
        rom_full_path = self._get_current_selected_rom()

        if not rom_full_path:
            return

        self._clipboard.setText(rom_full_path)


    def _games_list_copy_rom_filename(self):
        rom_full_path = self._get_current_selected_rom()

        if not rom_full_path:
            return

        self._clipboard.setText(os.path.basename(rom_full_path))


    def _games_list_google_game(self):
        system_game_name = self._get_current_system_n_game_name()

        if not system_game_name:
            return

        url = QtCore.QUrl('https://www.google.com/search?q={system_game_name}'.format(
            system_game_name=system_game_name
        ))

        QtGui.QDesktopServices.openUrl(url)


    def _games_list_current_row_changed(self):
        self._need_update_cover = True


    def _run_game_button_clicked(self):
        self._run_selected_game()


    def _antimicro_profile_button_clicked(self):
        self._switch_antimicro_profile(1)


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
