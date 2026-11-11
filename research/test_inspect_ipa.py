import io
import plistlib
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

from inspect_ipa import ARM64, inspect_ipa, inspect_macho


def executable(cryptid=0, endian="<", cpu=ARM64):
    header = struct.pack(endian + "IIIIIIII", 0xFEEDFACF, cpu, 0, 2, 1, 24, 0, 0)
    command = struct.pack(endian + "IIIIII", 0x2C, 24, 0, 0, cryptid, 0)
    return header + command


class MachOTests(unittest.TestCase):
    def test_detects_clear_and_encrypted_arm64(self):
        for flag in (0, 1, 7):
            with self.subTest(flag=flag):
                data = executable(flag)
                result = inspect_macho(io.BytesIO(data), len(data))[0]
                self.assertTrue(result["arm64"])
                self.assertEqual(result["encrypted"], flag != 0)

    def test_big_endian_executable(self):
        data = executable(1, ">")
        self.assertTrue(inspect_macho(io.BytesIO(data), len(data))[0]["encrypted"])

    def test_universal_32_and_64_bit_tables(self):
        first = executable(1, cpu=0x01000007)
        second = executable(0)
        for wide in (False, True):
            with self.subTest(wide=wide):
                row_format = ">IIQQII" if wide else ">IIIII"
                table_length = 8 + 2 * struct.calcsize(row_format)
                def row(cpu, offset, size):
                    values = [cpu, 0, offset, size, 0]
                    if wide:
                        values.append(0)
                    return struct.pack(row_format, *values)
                data = struct.pack(">II", 0xCAFEBABF if wide else 0xCAFEBABE, 2)
                data += row(0x01000007, table_length, len(first))
                data += row(ARM64, table_length + len(first), len(second))
                data += first + second
                result = inspect_macho(io.BytesIO(data), len(data))
                self.assertEqual(len(result), 2)
                self.assertTrue(result[0]["encrypted"])
                self.assertTrue(result[1]["arm64"])
                self.assertFalse(result[1]["encrypted"])

    def test_rejects_bad_command_length(self):
        data = bytearray(executable())
        struct.pack_into("<I", data, 36, 4)
        with self.assertRaisesRegex(ValueError, "command length"):
            inspect_macho(io.BytesIO(data), len(data))

    def test_rejects_truncated_and_unknown_files(self):
        for data in (b"", b"text", executable()[:-1]):
            with self.subTest(data=data[:4]), self.assertRaises(ValueError):
                inspect_macho(io.BytesIO(data), len(data))

    def test_rejects_out_of_bounds_fat_slice(self):
        data = struct.pack(">IIIIIII", 0xCAFEBABE, 1, ARM64, 0, 300, 40, 0)
        with self.assertRaisesRegex(ValueError, "architecture range"):
            inspect_macho(io.BytesIO(data), len(data))

    def test_rejects_architecture_mismatch(self):
        thin = executable()
        data = struct.pack(">IIIIIII", 0xCAFEBABE, 1, 0x01000007, 0, 28, len(thin), 0) + thin
        with self.assertRaisesRegex(ValueError, "disagrees"):
            inspect_macho(io.BytesIO(data), len(data))


class IPATests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "fixture.ipa"

    def tearDown(self):
        self.directory.cleanup()

    def create(self, info=None, encrypted=0):
        if info is None:
            info = {"CFBundleExecutable": "Fixture", "CFBundleIdentifier": "test.fixture", "CFBundleDisplayName": "Fixture"}
        with zipfile.ZipFile(self.path, "w") as archive:
            archive.writestr("Payload/Fixture.app/Info.plist", plistlib.dumps(info))
            archive.writestr("Payload/Fixture.app/Fixture", executable(encrypted))

    def test_reports_header_metadata_without_changing_archive(self):
        self.create(encrypted=1)
        original = self.path.read_bytes()
        result = inspect_ipa(self.path)
        self.assertEqual(result["bundle_id"], "test.fixture")
        self.assertTrue(result["main_executable_arm64_encrypted"])
        self.assertFalse(result["embedded_provision_present"])
        self.assertEqual(original, self.path.read_bytes())
        self.assertEqual(list(Path(self.directory.name).iterdir()), [self.path])

    def test_accepts_binary_plist(self):
        with zipfile.ZipFile(self.path, "w") as archive:
            archive.writestr("Payload/App.app/Info.plist", plistlib.dumps({"CFBundleExecutable": "App"}, fmt=plistlib.FMT_BINARY))
            archive.writestr("Payload/App.app/App", executable())
        self.assertFalse(inspect_ipa(self.path)["main_executable_arm64_encrypted"])

    def test_rejects_multiple_main_apps(self):
        self.create()
        with zipfile.ZipFile(self.path, "a") as archive:
            archive.writestr("Payload/Other.app/Info.plist", plistlib.dumps({}))
        with self.assertRaisesRegex(ValueError, "exactly one"):
            inspect_ipa(self.path)

    def test_rejects_traversal_executable(self):
        self.create({"CFBundleExecutable": "../Escape"})
        with self.assertRaisesRegex(ValueError, "CFBundleExecutable"):
            inspect_ipa(self.path)

    def test_rejects_non_dictionary_info(self):
        self.create(["invalid"])
        with self.assertRaisesRegex(ValueError, "dictionary"):
            inspect_ipa(self.path)


if __name__ == "__main__":
    unittest.main()
