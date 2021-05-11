'''
TODO：修改bcast
发起交易的人
'''
from key.signature import sign
from key.ecdsaKey import generate_ECDSA_keys
from message.message import createTransaction
import json

class User:
    def __init__(self, pubkey, privkey, deposit=0):
        self.username = pubkey
        self.privkey = privkey
        self.deposit = deposit

    def transfer(self, receiver, amount):
        transaction = createTransaction(self.username, receiver, amount)
        transaction["signature"] = sign(self.privkey, json.dumps(transaction["transaction_information"]))
        # TODO: broadcast transaction


# pub, priv = generate_ECDSA_keys()
# userA = User(pub, priv)
# userA.transfer("userB", 10)

