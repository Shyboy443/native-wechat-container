"""Read IPA metadata and Mach-O encryption headers without extracting or changing it."""

import argparse
import json
import plistlib
import struct
import zipfile
from pathlib import PurePosixPath


MAX_COMMAND_BYTES = 4 * 1024 * 1024
ARM64 = 0x0100000C


def read_exact(stream, offset, size, limit):
    if offset < 0 or size < 0 or offset + size > limit:
        raise ValueError("Mach-O data extends outside its file or architecture slice")
    stream.seek(offset)
    data = stream.read(size)
    if len(data) != size:
        raise ValueError("Truncated Mach-O data")
    return data


def inspect_slice(stream, offset, size):
    magic = read_exact(stream, offset, 4, offset + size)
    formats = {
        b"\xcf\xfa\xed\xfe": ("<", 32), b"\xfe\xed\xfa\xcf": (">", 32),
        b"\xce\xfa\xed\xfe": ("<", 28), b"\xfe\xed\xfa\xce": (">", 28),
    }
    if magic not in formats:
        raise ValueError("Unrecognized Mach-O architecture header")
    endian, header_size = formats[magic]
    header = read_exact(stream, offset, header_size, offset + size)
    cpu, _, filetype, count, command_bytes = struct.unpack_from(endian + "IIIII", header, 4)
    if command_bytes > MAX_COMMAND_BYTES or count > command_bytes // 8:
        raise ValueError("Invalid Mach-O load command table")
    commands = read_exact(stream, offset + header_size, command_bytes, offset + size)
    cursor, cryptids = 0, []
    for _ in range(count):
        if cursor + 8 > len(commands):
            raise ValueError("Truncated Mach-O load command")
        command, length = struct.unpack_from(endian + "II", commands, cursor)
        if length < 8 or cursor + length > len(commands):
            raise ValueError("Invalid Mach-O load command length")
        if command in (0x21, 0x2C):
            minimum = 24 if command == 0x2C else 20
            if length < minimum:
                raise ValueError("Truncated encryption command")
            cryptids.append(struct.unpack_from(endian + "I", commands, cursor + 16)[0])
        cursor += length
    if cursor != len(commands):
        raise ValueError("Load command count and size disagree")
    return {"cpu_type": cpu, "arm64": cpu == ARM64, "file_type": filetype,
            "encrypted": any(cryptids), "encryption_commands": len(cryptids)}


def inspect_macho(stream, size):
    magic = read_exact(stream, 0, 4, size)
    fat_formats = {b"\xca\xfe\xba\xbe": (">", False), b"\xbe\xba\xfe\xca": ("<", False),
                   b"\xca\xfe\xba\xbf": (">", True), b"\xbf\xba\xfe\xca": ("<", True)}
    if magic not in fat_formats:
        return [inspect_slice(stream, 0, size)]
    endian, wide = fat_formats[magic]
    count = struct.unpack(endian + "I", read_exact(stream, 4, 4, size))[0]
    if not 1 <= count <= 64:
        raise ValueError("Invalid universal Mach-O architecture count")
    row_size = 32 if wide else 20
    table_end = 8 + count * row_size
    table = read_exact(stream, 8, count * row_size, size)
    result, ranges = [], []
    for index in range(count):
        row = table[index * row_size:(index + 1) * row_size]
        cpu = struct.unpack_from(endian + "I", row)[0]
        offset, length = struct.unpack_from(endian + ("QQ" if wide else "II"), row, 8)
        if offset < table_end or length < 28 or offset + length > size:
            raise ValueError("Invalid universal Mach-O architecture range")
        if any(offset < end and offset + length > start for start, end in ranges):
            raise ValueError("Overlapping Mach-O architecture slices")
        ranges.append((offset, offset + length))
        item = inspect_slice(stream, offset, length)
        if item["cpu_type"] != cpu:
            raise ValueError("Architecture table disagrees with its Mach-O header")
        result.append(item)
    return result


def inspect_ipa(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("IPA contains duplicate ZIP entries")
        candidates = [name for name in names if len(PurePosixPath(name).parts) == 3
                      and name.startswith("Payload/") and PurePosixPath(name).parts[1].endswith(".app")
                      and PurePosixPath(name).name == "Info.plist"]
        if len(candidates) != 1:
            raise ValueError("Expected exactly one main app Info.plist in Payload")
        info_path = candidates[0]
        if archive.getinfo(info_path).file_size > 4 * 1024 * 1024:
            raise ValueError("App Info.plist exceeds the metadata size limit")
        info = plistlib.loads(archive.read(info_path))
        if not isinstance(info, dict):
            raise ValueError("App Info.plist must contain a dictionary")
        executable = info.get("CFBundleExecutable")
        if not isinstance(executable, str) or not executable or "/" in executable or "\\" in executable or executable in (".", ".."):
            raise ValueError("Invalid CFBundleExecutable")
        app_path = str(PurePosixPath(info_path).parent)
        executable_path = app_path + "/" + executable
        entry = archive.getinfo(executable_path)
        with archive.open(entry) as stream:
            slices = inspect_macho(stream, entry.file_size)
        arm64 = [item for item in slices if item["arm64"]]
        return {
            "name": info.get("CFBundleDisplayName", info.get("CFBundleName")),
            "bundle_id": info.get("CFBundleIdentifier"), "version": info.get("CFBundleShortVersionString"),
            "build": info.get("CFBundleVersion"), "minimum_ios": info.get("MinimumOSVersion"),
            "architectures": slices, "main_executable_arm64_present": bool(arm64),
            "main_executable_arm64_encrypted": any(item["encrypted"] for item in arm64) if arm64 else None,
            "embedded_provision_present": app_path + "/embedded.mobileprovision" in names,
            "code_resources_present": app_path + "/_CodeSignature/CodeResources" in names,
            "checks_remaining": ["embedded frameworks and extensions", "signature and entitlements validation",
                                 "physical-device launch", "WeChat account login", "two-account persistence", "notifications"],
            "assessment": "Header inspection only. Importability and runtime compatibility remain unverified."
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ipa", help="Path to the IPA to inspect locally")
    args = parser.parse_args()
    try:
        print(json.dumps(inspect_ipa(args.ipa), indent=2, ensure_ascii=False))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, plistlib.InvalidFileException) as error:
        parser.exit(1, f"Cannot inspect IPA: {error}\n")
