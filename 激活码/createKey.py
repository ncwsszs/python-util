import base64

from Crypto.Hash import SHA1, SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Util.asn1 import DerSequence, DerObjectId, DerNull, DerOctetString
from Crypto.Util.number import ceil_div
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


# noinspection PyTypeChecker
def pkcs15_encode(msg_hash, emLen, with_hash_parameters=True):
    """
    Implement the ``EMSA-PKCS1-V1_5-ENCODE`` function, as defined
    :param msg_hash: hash object
    :param emLen: int
    :param with_hash_parameters: bool
    :return: An ``emLen`` byte long string that encodes the hash.
    """
    digestAlgo = DerSequence([DerObjectId(msg_hash.oid).encode()])

    if with_hash_parameters:
        digestAlgo.append(DerNull().encode())

    digest = DerOctetString(msg_hash.digest())
    digestInfo = DerSequence([
        digestAlgo.encode(),
        digest.encode()
    ]).encode()

    # We need at least 11 bytes for the remaining data: 3 fixed bytes and
    # at least 8 bytes of padding).
    if emLen < len(digestInfo) + 11:
        raise TypeError("Selected hash algorithm has a too long digest (%d bytes)." % len(digest))
    PS = b'\xFF' * (emLen - len(digestInfo) - 3)
    return b'\x00\x01' + PS + b'\x00' + digestInfo


certBase64 = "MIIExTCCAq2gAwIBAgIUHwn5JtK1HfyyCyvYIatFpMRhygcwDQYJKoZIhvcNAQELBQAwGDEWMBQGA1UEAwwNSmV0UHJvZmlsZSBDQTAeFw0yNjAyMDQxNDIxNDRaFw0zNjAyMDMxNDIxNDRaMCExHzAdBgNVBAMMFk1vWXVuby1mcm9tLTIwMjItMDctMjUwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQDEcNUGWQZk/4rkU/Gf/uwdfYuwq3+P/tQPtsvu2bjojfwszjQ1p+IC0CNsYvqp4HwHFHUFYWHE1KHkXd/1+NYnNdeYwGV+JhsPQmdnlZbauMHB0KdlTTufIk5lNnpupVo0eT90kO/u6zCVDDnSXDlDpW9NA8Ygr7OKY5ah8rLwoqFhTWfUUQnBYZlAC97qycco5NEiydQgG4Ffala/pcVjQw/iDDXy8cZ+CFg9ZEVT8PeNqYnKDM1OIXPE95BzQC1NGQ3978egwKgAkU6Gl6cQDvWSdVhpNpRawi//5pfOhqLRcL6PscJ1sv51mXJ/N+u6n3dAaW2YZOpAmnluiAy+ebtm7SEpendGYhihjR+FFvCjI6dzxBbQQVRjPLqPWtOnO8qb2+wX5qXzOKP0bSPZIV9i4GgUKABe0cFZWRwz24nwlSU9RJK7247dM1D14eVghPlxAa+Rgjn2nDA2kfzar/1U07yRUPd3N9OknhYpszyRsHEs1ZhRc2rgVSVyvfKUe+6iGCfflWT3Fbn6rpu6VzK2hQsJBAjHiLjjrXDSygpzK8g+ibyjyd/fx/DEmysefjWkwdHjBfdiATeXz9x36Y+tq5t5f8wSixHS/ap/0LqrMA/glbi0m8p/sGFiToaZ9ld3mlj7fMfuyHT545GPDCnpmAci/3NBBun1ScXxjQIDAQABMA0GCSqGSIb3DQEBCwUAA4ICAQAsRNxZSeisUY05kZUU3v9W+1WcMBJDIs1QnO/9kLbp2UHBQKS7OfOKPMvNILQM47HpZpuVpUkkNJhR0I5LwbxoJfNDwcWKFPkPjBObk14O5Ttph64pHnE39ImPfsEWRAWbFnzgDD+Eo6sLtc1PUDnM+XUtqMGxROl6cQUkbQgopxgySKm/JGRB6fFBraHzOb4wboUkwRMg+DPa9eaLEyKyfOYz6i5ZoCBcteu2DaHU3IYPAU/TfOP4BFIxYZTwS4MNfYHY9eGiDVPlOIjYPKudPyXLtbYb/2p6CR/YRW8vLc659ypUNka0Ot/o0y60h1L1vtAtycL1DNc7E9Pqx4+ocGcQS/tbNBS8LHwx+TwvMexalWi25/xxlgZG+DGIyvwPqYVyXBSDf40bo8n437AqH+ag4XMOH8PKLDrNOneLiqFJRFl7hxiTNlg6+wpmwYRdvlrAEOE9kVeQFEeJdHNeMTc19hMcRtTqxNP1V5YmV3bv9qRSrG80UtDmvTdHh7mRTS6iCYs6u9fuorNMjpw6aNo9cnHAKgaYf14nGb/fwFdZwfHXPdcjsqMjNzhYa0sMu5kZkJ9D62yLD5WaLo32sG+7WqmsYYwdjLTFgjHr0UWoxW0KSWlcTsk+XGQ+5wQBJpaQGlQuXiZJiRs7z2f26EkFngAN7zwPn4tzJNNObA=="

cert = x509.load_der_x509_certificate(base64.b64decode(certBase64))
public_key = cert.public_key()
sign = int.from_bytes(cert.signature, byteorder="big", )
print(f"sign:{sign}")

modBits = public_key.key_size
digest_cert = SHA256.new(cert.tbs_certificate_bytes)
r = int.from_bytes(pkcs15_encode(digest_cert, ceil_div(modBits, 8)), byteorder='big', signed=False)
print(f"result:{r}")

licenseId = 'ZCB571FZHV'
licensePart = '{"licenseId": "ZCB571FZHV", "licenseeName": "MoYuno", "assigneeName": "", "assigneeEmail": "", "licenseRestriction": "", "checkConcurrentUse": false, "products": [{"code": "PDB", "fallbackDate": "2030-12-31", "paidUpTo": "2030-12-31", "extended": true}, {"code": "PSI", "fallbackDate": "2030-12-31", "paidUpTo": "2030-12-31", "extended": true}, {"code": "PPC", "fallbackDate": "2030-12-31", "paidUpTo": "2030-12-31", "extended": true}, {"code": "PCWMP", "fallbackDate": "2030-12-31", "paidUpTo": "2030-12-31", "extended": true}, {"code": "PPS", "fallbackDate": "2030-12-31", "paidUpTo": "2030-12-31", "extended": true}, {"code": "PRB", "fallbackDate": "2030-12-31", "paidUpTo": "2030-12-31", "extended": true}, {"code": "II", "fallbackDate": "2030-12-31", "paidUpTo": "2030-12-31", "extended": false}, {"code": "PGO", "fallbackDate": "2030-12-31", "paidUpTo": "2030-12-31", "extended": true}, {"code": "PSW", "fallbackDate": "2030-12-31", "paidUpTo": "2030-12-31", "extended": true}, {"code": "PWS", "fallbackDate": "2030-12-31", "paidUpTo": "2030-12-31", "extended": true}], "metadata": "0120220701PSAN000005", "hash": "TRIAL:-594988122", "gracePeriodDays": 7, "autoProlongated": false, "isAutoProlongated": false}'

digest = SHA1.new(licensePart.encode('utf-8'))

with open('ca.key') as prifile:
    private_key = RSA.import_key(prifile.read())
    # 使用私钥对HASH值进行签名
    signature = pkcs1_15.new(private_key).sign(digest)

    sig_results = base64.b64encode(signature)
    licensePartBase64 = base64.b64encode(bytes(licensePart.encode('utf-8')))
    public_key.verify(
        base64.b64decode(sig_results),
        base64.b64decode(licensePartBase64),
        padding=padding.PKCS1v15(),
        algorithm=hashes.SHA1(),
    )
    result = licenseId + "-" + licensePartBase64.decode('utf-8') + "-" + sig_results.decode('utf-8') + "-" + certBase64
    print(result)
