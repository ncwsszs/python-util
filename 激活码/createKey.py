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


certBase64 = "MIIExTCCAq2gAwIBAgIUCgypAAm58CtqKaBVJLFSVvyJqycwDQYJKoZIhvcNAQELBQAwGDEWMBQGA1UEAwwNSmV0UHJvZmlsZSBDQTAeFw0yNjAyMDQxNDQ3MTZaFw0zNjAyMDMxNDQ3MTZaMCExHzAdBgNVBAMMFk1vWXVuby1mcm9tLTIwMjItMDctMjUwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQD5Lup8pLRMPIKfdzWxpe5lVwUeWxf3viX/na2tHNMZIk9CZSZctpwq+tu/eNBVwn9OUPsicQGKZZngDtpTU2n+T3e0zZfMT2HZh4YibSSc0PI+kfW/OycCO9IM357FafhllBdhIy0K9cNwH51dJuOsNzIJx5AUBPfgQrVoRSfdsBQKD7Mh3XLN3l3cZoVXBEgX6e0WYjfGsoisRlSN32UK+Kz6xvU/AHN6d7v1AvQDrWbguIQ8RCNsd6H2vPsia6WpUYm/9aNjcBmanRDrgVc6krUb0byhdtPLKmd9lAlxhZs+5Cl/yqVInSbUZKMTOsC+pZMnaUcy7C6Gz7+fN6kSY5XccTXQ3Y09agv1S0SMFnXp+3X6OeN+njBLSrgLBlOS63FErDPTUY0I+yDVMARaxy8QooXhROorVnqZ4rgzR1UZysH5VKmdO4xncrhGIrXVS11CLyKe+6vH8q51jIGGE+nxIz5MIPwHH0sLPxEUAHtkumktP4+dMIEjlJ/6WveidxfjaFKaddIMAHaBpD3jFD+p7VS5xJ1vHP7SOqMP1Fcqy13eObcZT9kP1vb9lL1wZ9U+wyrrliyh3ZG/Cr2y8dryoQi+lQOCxA5ph1msTYhYMenhl/Ox2GDmuoOqI1Evw5OQU534YCd3otlxcPZVwCK+ujwMKeqqs7RuoWtVMwIDAQABMA0GCSqGSIb3DQEBCwUAA4ICAQAu77ClZcshsY/VcRkMDzqtoJcNTftPtqsiveJ7s5yE+A9L0qpv+lvJgx6iZwUo1h3Yjk7LRKW/VWYBHoYXbUXC0GXpion4IVUsnSfYcqgaqXtlJj+HGJiVMfCddrUwTn9P3WwlyytO6XPFMSMNGSf7wgAy6glmqqMaIqflKnOs4ob68sQO3xYbzEeYntkIvJxXyz6YoGUbV1INeyCP1QjElu3E8Kd1rcgc+T92ImsQlYfEw3RUf2frJ8PdfOaSSKmMc0Xnmf430UPoT1T3QKbTDpUyKVHjXD+w2fDgVZvDxYFxL20tw5D8xmTDfxYizLSvBifssknCkczMYopuJxNvcy+UupZmCSrQ7hZVt+qBOOoDDZPi6ci79Nin19nLqTsMW571eF9W7a8xdMTSjzR3AWwDNRBM0Z8uAphKZ56iK9RUmeHA//j2Fep5Ei0T8+mVB9qQc5+8VFBdPgzVdnrQy3gI4K8jYxHLwl0gPCSbYrqzl/g6Sj/AZgd3/qmDMBONultMqyJnJSuUsP7J9ZPyI8BXnEcrg5Sr7y07UawDZdJAWAq2Qghnlz1k7C1RfR7FBTvqP4jBdDYiV3IKk2srJsUA1P9AkfD3VzRH2NiOpD0ALDUgd7G+jNIuYv4bVZQUCnHbT0PKZgv9DjPbksK6BQss70bK0gxTiYz0EtU0HA=="

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
