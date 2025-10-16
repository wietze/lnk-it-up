# lnk-generator

A `python` module for generating deceptive LNK files.

## Introduction

TBD

## Installation

0. Make sure you have a recent version of `python` installed; it was created using python 3.12.3.
1. Download or clone the repository.
2. Open your favourite command shell and navigate to the repository's main folder.
3. Simply run `python3 -m lnk-generator.generate --help`.

## Usage

```text
Generate a deceptive LNK file. (C) @Wietze, 2025

positional arguments:
  {FAKE_IMAGE_PATH,DISABLE_NO_ARGUMENTS,OVERFLOW,FAKE_IMAGE_PATH_DISABLED}
                        FAKE_IMAGE_PATH          Spoof the target executable (command-line arguments will remain visible)
                        DISABLE_NO_ARGUMENTS     Disable the entire target field, only show target executable (command-line arguments are invisible)
                        OVERFLOW                 Spoof the target executable (command-line arguments will remain visible)
                        FAKE_IMAGE_PATH_DISABLED Spoof the target executable, disable the target field (command-line arguments are invisible)

options:
  -h, --help            show this help message and exit
  --output path/to/shortcut.lnk
                        The output path of the LNK on this system.

LNK target:
  --target-executable c:\path\to\file.exe
                        The path of the executable that should be executed.
  --target-command-line "/some /arguments"
                        Any command-line arguments for the target executable.
  --fake-path c:\path\to\fake_file.exe
                        A spoofed path that will be displayed in the LNK's target field.

LNK icon:
  --icon c:\path\to\icon.ico
                        A path to a .ico file that will be used as the LNK file's icon. Supports environment variables.
  --icon-index n        The index within the specified icon file that holds the icon the LNK file should display.
```
