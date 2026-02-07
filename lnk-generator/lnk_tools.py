from enum import IntEnum

from .byte_tools import ByteTools

# Copyright, 2023-2025
# Reference: https://winprotocoldocs-bhdugrdyduf5h2e4.b02.azurefd.net/MS-SHLLINK/%5bMS-SHLLINK%5d.pdf

ANSI_ENCODING = 'cp1252' # Windows-1252

class SHELL_LINK_HEADER:
    HeaderSize = ByteTools.create_bytes(0x4C, 4)
    LinkCLSID = ByteTools.create_bytes(0x46000000000000c00000000000021401, 16)

    class LinkFlags(IntEnum):
        IGNORE = 0x00
        HasLinkTargetIDList = 0x01
        HasLinkInfo = 0x02
        HasName = 0x04
        HasRelativePath = 0x08
        HasWorkingDir = 0x10
        HasArguments = 0x20
        HasIconLocation = 0x40
        IsUnicode = 0x80
        ForceNoLinkInfo = 0x0100
        HasExpString = 0x0200
        RunInSeparateProcess = 0x0400
        Reserved0 = 0x0800
        HasDarwinId = 0x1000
        RunAsUser = 0x2000
        HasExpIcon = 0x4000
        NoPidlAlias = 0x8000
        Reserved1 = 0x010000
        RunWithShimLayer = 0x020000
        ForceNoLinkTrack = 0x040000
        EnableTargetMetadata = 0x080000
        DisableLinkPathTracking = 0x100000
        DisableKnownFolderTracking = 0x200000
        DisableKnownFolderAlias = 0x400000
        AllowLinkToLink = 0x800000
        UnaliasOnSave = 0x01000000
        PreferEnvironmentPath = 0x02000000
        KeepLocalIdListForUncTarget = 0x04000000

    class FileAttributes(IntEnum):
        FILE_ATTRIBUTE_READONLY = 0x01
        FILE_ATTRIBUTE_HIDDEN = 0x02
        FILE_ATTRIBUTE_SYSTEM = 0x04
        Reserved1 = 0x08
        FILE_ATTRIBUTE_DIRECTORY = 0x10
        FILE_ATTRIBUTE_ARCHIVE = 0x20
        Reserved2 = 0x40
        FILE_ATTRIBUTE_NORMAL = 0x80
        FILE_ATTRIBUTE_TEMPORARY = 0x0100
        FILE_ATTRIBUTE_SPARSE_FILE = 0x0200
        FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
        FILE_ATTRIBUTE_COMPRESSED = 0x0800
        FILE_ATTRIBUTE_OFFLINE = 0x1000
        FILE_ATTRIBUTE_NOT_CONTENT_INDEXED = 0x2000
        FILE_ATTRIBUTE_ENCRYPTED = 0x4000

    class ShowCommand(IntEnum):
        SW_SHOWNORMAL = 0x01
        SW_SHOWMAXIMIZED = 0x03
        SW_SHOWMINNOACTIVE = 0x07

    @classmethod
    def write(cls, link_flags: list[LinkFlags] | int, file_attributes: list[FileAttributes], show_command: ShowCommand, icon_index: int = 0) -> bytes:
        # Taken from section 2.1
        return (cls.HeaderSize +
                cls.LinkCLSID +
                ByteTools.create_bytes(link_flags if isinstance(link_flags, int) else ByteTools.resolve(link_flags), 4) +
                ByteTools.create_bytes(ByteTools.resolve(file_attributes), 4) +
                # CreationTime, AccessTime, WriteTime
                (ByteTools.create_bytes(0x00, 8) * 3) +
                # FileSize
                ByteTools.create_bytes(0x00, 4) +
                ByteTools.create_bytes(icon_index, 4) +
                ByteTools.create_bytes(show_command, 4) +
                # HotKey
                ByteTools.create_bytes(0x00, 2) +
                # Reserved 1
                ByteTools.create_bytes(0x00, 2) +
                # Reserved 2
                ByteTools.create_bytes(0x00, 4) +
                # Reserved 3
                ByteTools.create_bytes(0x00, 4))


class LINKTARGET_IDLIST:
    class ItemID:
        def __init__(self, target: bytes) -> None:
            self.target = target
            self.size = len(self.target) + 2

        def to_bytes(self) -> bytes:
            return ByteTools.create_bytes(self.size, 2) + self.target

    IDList: list[ItemID]

    def __init__(self, targets: list[ItemID]) -> None:
        self.IDList = targets

    def IDListSize(self) -> int: return sum(x.size for x in self.IDList)

    def write(self) -> bytes:
        # Taken from section 2.2
        return ByteTools.create_bytes(self.IDListSize() + 2, 2) + \
            b''.join(item_id.to_bytes() for item_id in self.IDList) + \
            ByteTools.create_bytes(0x00, 2)

    @staticmethod
    def path_to_idlist(path: str):
        path_parts = path.split('\\')

        if not path or len(path) <= 2 or not path[1] == ':' or not path[2] == '\\':
            raise ValueError('expecting a path starting with c:\\, d:\\, etc.; got %s instead' % path)

        folders = path_parts[1:-1] if '.' in path_parts[-1] else path_parts[1:]

        result = ([LINKTARGET_IDLIST.ItemID(ITEM.COMPUTER), LINKTARGET_IDLIST.ItemID(b'/'+path[0].encode(ANSI_ENCODING) + b':\\'+(b'\x00' * 22))] +
                  [LINKTARGET_IDLIST.ItemID(ITEM.generate_folder(part)) for part in folders])
        if '.' in path_parts[-1]:
            result += [LINKTARGET_IDLIST.ItemID(ITEM.generate_file(path_parts[-1]))]

        return result


class ITEM:
    COMPUTER = ByteTools.bytearray([0x1F, 0x50, 0xE0, 0x4F, 0xD0, 0x20, 0xEA, 0x3A, 0x69, 0x10, 0xA2, 0xD8, 0x08, 0x00, 0x2B, 0x30, 0x30, 0x9D])
    C_DRIVE = ByteTools.bytearray([0x2F, 0x43, 0x3A, 0x5C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    NETWORK = ByteTools.bytearray([0x1f, 0x58, 0x60, 0x2c, 0x8d, 0x20, 0xea, 0x3a, 0x69, 0x10, 0xa2, 0xd7, 0x08, 0x00, 0x2b, 0x30, 0x30, 0x9d])
    NETWORK_PROVIDER = ByteTools.bytearray([0x47, 0x00, 0x02, 0x45, 0x6e, 0x74, 0x69, 0x72, 0x65, 0x20, 0x4e, 0x65, 0x74, 0x77, 0x6f, 0x72, 0x6b, 0x00])
    WINDOWS_NETWORK = ByteTools.bytearray([0x46, 0x01, 0x82, 0x57, 0x65, 0x62, 0x20, 0x43, 0x6c, 0x69, 0x65, 0x6e, 0x74, 0x20, 0x4e, 0x65, 0x74, 0x77, 0x6f, 0x72, 0x6b, 0x00])  # + WEB_CLIENT_NETWORK
    # WEB_CLIENT_NETWORK = ByteTools.bytearray([0x57, 0x65, 0x62, 0x20, 0x43, 0x6c, 0x69, 0x65, 0x6e, 0x74, 0x20, 0x4e, 0x65, 0x74, 0x77, 0x6f, 0x72, 0x6b, 0x00, 0x2E, 0x00])

    @staticmethod
    def generate_unc_path(path: str) -> bytes:
        return ByteTools.bytearray([0x42, 0x01, 0x00]) + path.encode(ANSI_ENCODING) + ByteTools.create_bytes(0x00, 1)

    @staticmethod
    def generate_network_path(path: str) -> bytes:
        return ByteTools.bytearray([0xc3, 0x01, 0x00]) + path.encode(ANSI_ENCODING) + ByteTools.create_bytes(0x00, 1)

    @staticmethod
    def generate_folder(folder_name: str) -> bytes:
        return (ByteTools.create_bytes(0x35, 2) + # 0x30 | 0x01 (IS_DIRECTORY) | 0x04 (UNICODE)
            ByteTools.create_bytes(0x00, 4) + # File size set to 0
            ByteTools.create_bytes(0x00, 4) + # Last modification date and time set to 0
            ByteTools.create_bytes(0x10, 2) + # File attribute flags set to FILE_ATTRIBUTE_DIRECTORY
            folder_name.encode('utf-16le') + ByteTools.create_bytes(0x00, 2))

    @staticmethod
    def generate_file(file_name: str) -> bytes:
        return (ByteTools.create_bytes(0x36, 2) + # 0x30 | 0x02 (IS_FILE) | 0x04 (UNICODE)
            ByteTools.create_bytes(0x00, 4) + # File size set to 0
            ByteTools.create_bytes(0x00, 4) + # Last modification date and time set to 0
            ByteTools.create_bytes(0x80, 2) + # File attribute flags set to FILE_NORMAL
            file_name.encode('utf-16le') + ByteTools.create_bytes(0x00, 2))


class LINK_INFO:
    class LinkInfoFlags(IntEnum):
        VolumeIDAndLocalBasePath = 1
        CommonNetworkRelativeLinkAndPathSuffix = 2

    class VolumeId:
        DriveType = 0x03  # DRIVE_FIXED
        DriveSerial = 0xBADC0DED
        VolumeLabelOffset = 0x10
        Data = ""

        def write(self) -> bytes:
            # Taken from section 2.3.1
            result = (
                ByteTools.create_bytes(self.DriveType, 4) +
                ByteTools.create_bytes(self.DriveSerial, 4) +
                ByteTools.create_bytes(self.VolumeLabelOffset, 4) +
                self.Data.encode('utf-16le') + ByteTools.create_bytes(0x00, 1)
            )

            return ByteTools.create_bytes(len(result)+4, 4) + result

    class NetworkRelativeLink:
        CommonNetworkRelativeLinkFlags = 0x02  # ValidNetType

        def write(self, dest: str) -> bytes:
            path = dest.rsplit('\\', 1)[0]
            # Taken from section 2.3.2
            result = (
                # CommonNetworkRelativeLinkFlags
                ByteTools.create_bytes(self.CommonNetworkRelativeLinkFlags, 4)
                # NetNameOffset
                + ByteTools.create_bytes(0x14, 4)
                # DeviceNameOffset
                + ByteTools.create_bytes(0x00, 4) \
                # NetworkProviderType (WNNC_NET_DAV)
                + ByteTools.create_bytes(0x002E0000, 4) \
                # NetName
                + path.encode(ANSI_ENCODING) + ByteTools.create_bytes(0x00, 1)
            )

            return ByteTools.create_bytes(len(result)+4, 4) + result

    @classmethod
    def write(cls, link_info_flags: list[LinkInfoFlags], path: str) -> bytes:
        # Taken from section 2.3
        volume_block = LINK_INFO.VolumeId().write() if LINK_INFO.LinkInfoFlags.VolumeIDAndLocalBasePath in link_info_flags else LINK_INFO.NetworkRelativeLink().write(path)
        common_path_suffix = (path.encode(ANSI_ENCODING) if LINK_INFO.LinkInfoFlags.VolumeIDAndLocalBasePath in link_info_flags else path.rsplit('\\', 1)[-1].encode(ANSI_ENCODING)) + ByteTools.create_bytes(0x00, 1)
        result = (
            ByteTools.create_bytes(ByteTools.resolve(link_info_flags), 4) + # VolumeIDOffset (fixed)
            ByteTools.create_bytes(0x1C if LINK_INFO.LinkInfoFlags.VolumeIDAndLocalBasePath in link_info_flags else 0, 4) + # LocalBasePathOffset
            ByteTools.create_bytes(28 if LINK_INFO.LinkInfoFlags.VolumeIDAndLocalBasePath in link_info_flags else 0, 4) + # CommonNetworkRelativeLinkOffset
            ByteTools.create_bytes(28 if LINK_INFO.LinkInfoFlags.CommonNetworkRelativeLinkAndPathSuffix in link_info_flags else 0, 4) + # CommonPathSuffixOffset
            (ByteTools.create_bytes(28+len(volume_block), 4) if LINK_INFO.LinkInfoFlags.VolumeIDAndLocalBasePath else b'') + # LocalBasePath/CommonNetworkRelativeLink
            volume_block +
            common_path_suffix)

        return (
            # LinkInfoSize
            ByteTools.create_bytes(len(result) + 8, 4) +
            # LinkInfoHeaderSize (offsets to optional fields are NOT specified)
            ByteTools.create_bytes(0x1C, 4) +
            result)

    @classmethod
    def write_breaking(cls) -> bytes:
        network_block = LINK_INFO.NetworkRelativeLink().write("path")
        result = ByteTools.create_bytes(1, 4) + \
            ByteTools.create_bytes(0x00, 4) + \
            ByteTools.create_bytes(0x00, 4) + \
            ByteTools.create_bytes(0x1C, 4) + \
            ByteTools.create_bytes(0x1C + len(network_block), 4) + \
            network_block + \
            "\\".rsplit('\\', 1)[-1].encode(ANSI_ENCODING) + \
            ByteTools.create_bytes(0x00, 1)

        return ByteTools.create_bytes(len(result) + 8, 4) + \
            ByteTools.create_bytes(0x1C, 4) + result
