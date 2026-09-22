"""Synthetic CA/leaf fixtures only; not a production certificate installer."""
from datetime import datetime, timedelta, timezone
import ipaddress
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from m2_certificates import create


def authority(directory):
    directory=Path(directory); create(directory)  # Exclusive paths and protected key ACL.
    key=serialization.load_pem_private_key((directory/'key.pem').read_bytes(),None)
    name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Synthetic NDX fixture CA')])
    now=datetime.now(timezone.utc)
    cert=(x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
          .serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(days=1))
          .not_valid_after(now+timedelta(days=7))
          .add_extension(x509.BasicConstraints(ca=True,path_length=0),critical=True)
          .add_extension(x509.KeyUsage(False,False,False,False,False,True,True,None,None),critical=True)
          .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()),critical=False)
          .sign(key,hashes.SHA256()))
    (directory/'trust.pem').write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    return cert,key


def leaf(directory, issuer, expired=False, wrong_host=False):
    directory=Path(directory); create(directory)
    key=serialization.load_pem_private_key((directory/'key.pem').read_bytes(),None)
    ca,ca_key=issuer; now=datetime.now(timezone.utc)
    names=[x509.DNSName('wrong.invalid')] if wrong_host else [x509.DNSName('localhost'),x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]
    cert=(x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Synthetic NDX leaf')]))
          .issuer_name(ca.subject).public_key(key.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(now-timedelta(days=2)).not_valid_after(now-timedelta(days=1) if expired else now+timedelta(days=2))
          .add_extension(x509.BasicConstraints(ca=False,path_length=None),critical=True)
          .add_extension(x509.KeyUsage(True,False,True,False,False,False,False,None,None),critical=True)
          .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),critical=False)
          .add_extension(x509.SubjectAlternativeName(names),critical=False)
          .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()),critical=False)
          .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),critical=False)
          .sign(ca_key,hashes.SHA256()))
    (directory/'trust.pem').write_bytes(cert.public_bytes(serialization.Encoding.PEM))
