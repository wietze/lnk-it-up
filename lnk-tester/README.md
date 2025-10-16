# lnk-tester

A C++ program for identifying deceptive LNK files.

## Usage

TBD

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
   # For others, see https://www.mingw-w64.org/downloads/
   ```

2. Compile the executable as x64 binary:

   ```bash
   x86_64-w64-mingw32-g++ -o lnk-tester.exe lnk-tester.cpp -lole32 -luuid
   ```

### Windows

1. In Visual Studio's Developer Command Prompt (x64), run:

   ```bat
   cl /EHsc /Fe:lnk-tester.exe lnk-tester.cpp
   ```
