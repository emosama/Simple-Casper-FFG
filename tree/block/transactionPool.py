from tree.block.block import Block
class TransactionPool:
    def __init__(self):
        self.transaction_pool = []

    def initBlock(self, previous_hash):
        transaction = self.transaction_pool.pop(0)
        transactions = []
        while not (transaction == None or len(transactions) == 10):
            transactions.append(transaction)
        block = Block(transactions,previous_hash)
        return block

    def addTransaction(self,transaction):
        self.transaction_pool.append(transaction)

