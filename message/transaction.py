'''
已完成
'''
from key.signature import validateSignature, sign
from serialization.serialization import toString
class TransactionInformation:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.transaction_information = TransactionInformation(sender, receiver, amount)
        self.signature = ""

    def __init__(self, transaction_information):
        self.transaction_information = transaction_information
        self.signature = ""

    def sign(self, privkey):
        self.signature = sign(privkey, toString(self.transaction_information))

    def validate(self):
        return validateSignature(self.sender, self.signature, toString(self.transaction_information))
