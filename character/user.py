'''
TODO：修改bcast
发起交易的人
'''
from message.transaction import Transaction
class user:
    def __init__(self,pubkey, deposit = 0):
        self.username = pubkey
        self.deposit = deposit

    def transfer(self, receiver, amount, privkey):
        transaction = Transaction(self.username, receiver, amount)
        transaction.sign(privkey)

        # TODO: broadcast transaction


