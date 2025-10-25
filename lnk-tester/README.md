# lnk-tester

A C++ program for identifying deceptive LNK files.

## Usage

To check whether a given LNK file resolves to the expected target, run the following on a Windows machine:

```bat
lnk-tester.exe "path\to\a\shortcut.lnk"
```

An empty output with status code 0 indicates the LNK file's expected target path matches the resolved target path. This suggets the file has NOT been tempered with in a 'deceptive' way.

A non-empty output with status code 1 means the LNK file's expected target path does not match the resolved path. This suggests the file may have been tempared with in order to deceive the user.

A non-empty output with status code 2 means something went wrong while parsing the LNK file.

Optionally, specify `-v` as the last argument to see more verbose details, including the target paths observed and expected.

![Screenshot of a lnk-tester.exe execution.](/docs/lnk-tester.png)

## Compilation

### Linux / macOS

1. To compile in a *nix system, install the correct `mingw` package:

   ```bash
   # Debian
   apt install g++-mingw-w64-x86-64
   # Fedora
   dnf install mingw64-gcc-c++
   # Arch
   pacman -S mingw-w64-gcc
   # macOS
   brew install mingw-w64

   # For other platforms, see https://www.mingw-w64.org/downloads/
   ```

2. Compile the executable as x64 binary:

   ```bash
   x86_64-w64-mingw32-g++ -o lnk-tester.exe lnk-tester.cpp -lole32 -luuid
   ```

### Windows

1. Make sure Visual Studio is installed.

2. In Visual Studio's Developer Command Prompt (x64), run:

   ```bat
   cl /EHsc /Fe:lnk-tester.exe lnk-tester.cpp
   ```
