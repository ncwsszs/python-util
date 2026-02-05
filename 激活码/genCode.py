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
    Implement the ``EMSA-PKCS1-V1_5-ENCODE`` function, as defined EMSA-PKCS1-V1_5-ENCODE
    :param msg_hash: hash object
    :param emLen: int
    :param with_hash_parameters: bool
    :return: An ``emLen`` byte long string that encodes the hash.
    """

    digestAlgo = DerSequence([DerObjectId(msg_hash.oid).encode()])



    if with_hash_parameters:
        digestAlgo.append(DerNull().encode())


    md=msg_hash.digest()
    digest = DerOctetString(md)
    digestInfo = DerSequence([digestAlgo.encode(),digest.encode()]).encode()


    # We need at least 11 bytes for the remaining data: 3 fixed bytes and
    # at least 8 bytes of padding).
    if emLen < len(digestInfo) + 11:
        raise TypeError("Selected hash algorithm has a too long digest (%d bytes)." % len(digest))
    PS = b'\xFF' * (emLen - len(digestInfo) - 3)
    resdi= b'\x00\x01' + PS + b'\x00' + digestInfo


    print(f"res:{base64.b64encode(resdi).decode('utf-8')}")
    print(f"md:{base64.b64encode(md).decode('utf-8')}")


    return resdi


# 用于存储证书内容的字符串
certificate_content = ""

# 用于标记是否已经开始读取证书内容
reading_certificate = False

# 打开源文件并逐行读取
with open('../ca.crt', 'r', encoding='utf-8') as file:
    for line in file:
        # 去掉行尾的换行符
        line = line.strip()

        # 检查是否是证书开始标记
        if line == "-----BEGIN CERTIFICATE-----":
            reading_certificate = True
            continue

        # 检查是否是证书结束标记
        if line == "-----END CERTIFICATE-----":
            reading_certificate = False
            break

        # 如果已经在读取证书内容
        if reading_certificate:
            certificate_content += line

# 输出结果
#print(certificate_content)

certBase64 = certificate_content


cert = x509.load_der_x509_certificate(base64.b64decode(certBase64))
public_key = cert.public_key()
sign = int.from_bytes(cert.signature, byteorder="big", )
#print(f"sign:{sign}")

modBits = public_key.key_size


digest_cert = SHA256.new(cert.tbs_certificate_bytes)
r = int.from_bytes(pkcs15_encode(digest_cert, ceil_div(modBits, 8)), byteorder='big', signed=False)
print(f"result:{r}")

# 模幂运算指数
modIndex = '65537'

# jetbrains内置root证书的公钥的模
rootCertVersion1 = '860106576952879101192782278876319243486072481962999610484027161162448933268423045647258145695082284265933019120714643752088997312766689988016808929265129401027490891810902278465065056686129972085119605237470899952751915070244375173428976413406363879128531449407795115913715863867259163957682164040613505040314747660800424242248055421184038777878268502955477482203711835548014501087778959157112423823275878824729132393281517778742463067583320091009916141454657614089600126948087954465055321987012989937065785013284988096504657892738536613208311013047138019418152103262155848541574327484510025594166239784429845180875774012229784878903603491426732347994359380330103328705981064044872334790365894924494923595382470094461546336020961505275530597716457288511366082299255537762891238136381924520749228412559219346777184174219999640906007205260040707839706131662149325151230558316068068139406816080119906833578907759960298749494098180107991752250725928647349597506532778539709852254478061194098069801549845163358315116260915270480057699929968468068015735162890213859113563672040630687357054902747438421559817252127187138838514773245413540030800888215961904267348727206110582505606182944023582459006406137831940959195566364811905585377246353'
rootCertVersion2 = '24156627931985958051017183040835577271803742470193804806479316178045088981962804168393398987646446251087541768081971475544151551235525470790716604369379805327668466429966167642117961353233058515180243264560201783520956161510523416923017697354365782825500659342029196527776056976223174394946371372849906309277537461992299774200098515526818746947230488275456663264920440977381968978227273889068919338259949793686590492904029279861913225794809675826299753284990778166519152326723946780528965868736869495336993456735232755342913885746267768375682771655854436236934171901662660193080235109535758464079136573948168636773471'

# 通用参数替换
commonArgsStr = 'EQUAL,65537,24773058818499217187577663886010908531303294206336895556072197892590450942803807164562754911175164262596715237551312004078542654996496301487027034803410086499747369353221485073240039340641397198525027728751956658900801359887190562885573922317930300068615009483578963467556425525328780085523172495307229112069939166202511721671904748968934606589702999279663332403655662225374084460291376706916679151764149324177444374590606643838366605181996272409014933080082205048098737253668016260658830645459388519595314928290853199112791333551144805347785109465401055719331231478162870216035573012645710763533896540021550083104281->3,24773058818499217187577663886010908531303294206336895556072197892590450942803807164562754911175164262596715237551312004078542654996496301487027034803410086499747369353221485073240039340641397198525027728751956658900801359887190562885573922317930300068615009483578963467556425525328780085523172495307229112069939166202511721671904748968934606589702999279663332403655662225374084460291376706916679151764149324177444374590606643838366605181996272409014933080082205048098737253668016260658830645459388519595314928290853199112791333551144805347785109465401055719331231478162870216035573012645710763533896540021550083104281'

power = '[Result]' + "\n" + '; Suit 230914' + "\n"
power += 'EQUAL,' + str(sign) + ',' + modIndex + ',' + rootCertVersion1 + '->' + str(r) + "\n"
power += 'EQUAL,' + str(sign) + ',' + modIndex + ',' + rootCertVersion2 + '->' + str(r) + "\n"
power += "\n"
power += '[Args]' + "\n"
power += commonArgsStr
# print(power)

# 打开文件
with open('../power.conf', 'w', encoding='utf-8') as file:
    # 写入字符串
    file.write(power)

print("write into power.conf")

licenseId = 'FV8EM46DQYC5AW9'
licensePart = '{"licenseId":"FV8EM46DQYC5AW9","licenseeName":"Vpen","licenseeType":"PERSONAL","assigneeName":"","assigneeEmail":"","licenseRestriction":"","checkConcurrentUse":false,"products":[{"code":"GO","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"RS0","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"DM","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"CL","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"RSU","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"RSC","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":true},{"code":"PC","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"DS","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"RD","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"RC","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"RSF","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":true},{"code":"RM","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"II","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"DPN","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"DB","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"DC","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"PS","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"RSV","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":true},{"code":"WS","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":false},{"code":"PSI","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":true},{"code":"PCWMP","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":true},{"code":"RS","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":true},{"code":"DP","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":true},{"code":"PDB","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":true},{"code":"PRR","fallbackDate":"2026-09-14","paidUpTo":"2026-09-14","extended":true}],"metadata":"0220240702PSAX000005X","hash":"12345678/0-541816629","gracePeriodDays":7,"autoProlongated":false,"isAutoProlongated":false,"trial":false,"aiAllowed":true}'

digest = SHA1.new(licensePart.encode('utf-8'))

with open('../ca.key') as prifile:
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
    print("-----")
    print(f"{licensePartBase64.decode('utf-8')}")
    print("-----")
    print(sig_results.decode('utf-8'))
    print("-----")
    print(result)


# 打开文件
with open('../activeCode.txt', 'w', encoding='utf-8') as file:
    # 写入字符串
    file.write(result)

print("write into activeCode.txt")
