"""Reproducibly patch iLoader 2.4.1's standalone LiveContainer certificate handoff."""
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tarfile
import urllib.request

CHECKSUM = '7cab6348bffd8f32c9358b80c8723bc1da45ad97b0c1f30a1533ade22d4d9496'


def replace_once(text, before, after):
    if text.count(before) != 1:
        raise ValueError('Upstream source changed; refusing an ambiguous patch')
    return text.replace(before, after, 1)


def prepare(installer):
    installer = installer.resolve()
    crate = installer.parent / 'isideload-container-fix'
    if crate.exists():
        raise FileExistsError('Use a fresh build directory; patched dependency already exists')
    data = urllib.request.urlopen(
        'https://crates.io/api/v1/crates/isideload/0.5.2/download', timeout=60).read()
    if hashlib.sha256(data).hexdigest() != CHECKSUM:
        raise ValueError('Dependency archive checksum mismatch')
    crate.mkdir()
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError('Unexpected link in dependency archive')
            relative = Path(member.name).relative_to('isideload-0.5.2')
            target = crate / relative
            if not target.resolve().is_relative_to(crate):
                raise ValueError('Unsafe dependency archive path')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())
    source = crate / 'src/sideload/application.rs'
    text = source.read_text(encoding='utf-8')
    text = replace_once(text,
        'SpecialApp::SideStoreLc\n                | SpecialApp::SideStore',
        'SpecialApp::SideStoreLc\n                | SpecialApp::LiveContainer\n                | SpecialApp::SideStore')
    text = replace_once(text, '            info!("Injecting certificate for {}", special);', '''            // Only the user's device-specific signed copy receives this key.
            if matches!(special, SpecialApp::LiveContainer) {
                if cert.machine_id.is_empty() {
                    bail!("The signing certificate has no machine ID; refusing an empty PKCS#12 password");
                }
                self.bundle.app_info.insert(
                    "LCInstallerCertificatePassword".to_string(),
                    plist::Value::String(cert.machine_id.clone()),
                );
            }
            info!("Injecting certificate for {}", special);''')
    source.write_text(text, encoding='utf-8')
    cargo = installer / 'src-tauri/Cargo.toml'
    with cargo.open('a', encoding='utf-8') as f:
        f.write('\n[patch.crates-io]\nisideload = { path = "../../isideload-container-fix" }\n')
    config = installer / 'src-tauri/tauri.conf.json'
    value = json.loads(config.read_text())
    value['productName'] = 'AccountContainer Installer'
    value['identifier'] = 'app.accountcontainer.installer'
    value['app']['windows'][0]['title'] = 'AccountContainer Installer - unofficial iLoader certificate fix'
    value['plugins']['updater']['endpoints'] = []
    value['plugins']['updater']['pubkey'] = ''
    value['bundle']['createUpdaterArtifacts'] = False
    config.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    tests = crate / 'tests'
    tests.mkdir(exist_ok=True)
    shutil.copyfile(Path(__file__).with_name('certificate_handoff.rs'), tests / 'certificate_handoff.rs')
    with (crate / 'Cargo.toml').open('a', encoding='utf-8') as f:
        f.write('\n[[test]]\nname = "certificate_handoff"\npath = "tests/certificate_handoff.rs"\n')
    print('Patched pinned isideload 0.5.2; standalone LiveContainer now receives its signing identity.')


if __name__ == '__main__':
    prepare(Path(sys.argv[1]))
