'''
已完成
'''

import base64
import ecdsa

def sign(privkey, msg):
    bmessage = msg.encode()
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(privkey), curve=ecdsa.SECP256k1)
    signature = base64.b64encode(sk.sign(bmessage))
    return signature.decode()

def validateSignature(pubkey, signature, msg):
    public_key = (base64.b64decode(pubkey)).hex()
    signature = base64.b64decode(signature)
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
    try:
        return vk.verify(signature, msg.encode())
    except:
        return False
