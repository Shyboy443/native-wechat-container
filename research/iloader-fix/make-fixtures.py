"""Generate disposable self-signed test identities, never real Apple signing keys."""
import datetime
from pathlib import Path
import sys
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

directory = Path(sys.argv[1]); directory.mkdir(parents=True, exist_ok=True)
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Container fixture only'),
                  x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, 'FIXTURETEAM')])
now = datetime.datetime.now(datetime.timezone.utc)
cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
        .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=1)).sign(key, hashes.SHA256()))
(directory / 'key.der').write_bytes(key.private_bytes(serialization.Encoding.DER,
    serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
(directory / 'cert.der').write_bytes(cert.public_bytes(serialization.Encoding.DER))
(directory / 'native-test.p12').write_bytes(pkcs12.serialize_key_and_certificates(
    b'fixture', key, cert, None, serialization.BestAvailableEncryption(b'local-fixture-password')))
print('Created disposable synthetic fixture identity.')
