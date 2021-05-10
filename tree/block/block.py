'''
已完成
the block of pow
'''
import hashlib
from serialization.serialization import toString

class BlockInformation:
    def __init__(self, transactions, previousHash):
        self.previousHash = previousHash
        self.transactions = transactions
        self.proof = ''

class Block:
    # Constructor
    def __init__(self, transactions, previousHash):
        self.block_information = BlockInformation(transactions, previousHash)
        self.hash = ''
        self.height = 0
        self.timestamp = ''


    def __init__(self, block_information):
        self.block_information = block_information
        self.hash = ''
        self.height = 0
        self.timestamp = ''

    # Compute hash (sha256)
    def computeHash(self):
        self.hash = hashlib.sha256((toString(self.block_information)).encode('utf-8')).hexdigest()
        return str(self.hash)

    def set_height(self,height):
        self.height = height
    #Set up the timestamp for block accepted
    def setTimestamp(self,time):
        self.timestamp = time

    # Check block before submit it
    def validate(self):
        assert self.hash == self.computeHash(), "The information of this block is changed"
        for transaction in self.block_information.transactions:
            transaction.validate() # 验证每一个transaction签名
        return True
    '''
    new add:
    '''
    def getDataForHash(self):
        return toString(self.block_information)

