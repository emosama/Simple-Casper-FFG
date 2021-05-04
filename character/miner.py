'''
TODO：修改bcast
矿工
'''

from proposalMechanism.pow import proofOfWork
from tree.block.block import Block
from message.transaction import Transaction

# the chain of blockchain
class Miner:
    def __init__(self, difficulty = 1):
        self.chain = [self.bigBang()]
        self.pow = proofOfWork(difficulty)
        self.transactionPool = []
        self.allocatedTransactions = []
        self.minerReward = 50

    def bigBang(self):
        genesisBlock = Block([Transaction("y3w","y3w","genesis block")],'')
        genesisBlock.hash = genesisBlock.computeHash()
        return genesisBlock

    # 暂定每个block最多10个transaction
    def allocateTransactions(self):
        while len(self.transactionPool) > 0 and len(self.allocatedTransactions) < 10:
            transaction = self.transactionPool.pop(0)
            self.allocatedTransactions.append(transaction)

    def getLatestBlock(self):
        return self.chain[-1]

    # Add block to chain
    def addBlockToChain(self,newBlock):
        ## Find the hash of the least block
        newBlock.previousHash = self.getLatestBlock().hash
        #newBlock.hash = newBlock.computeHash()

        ## Need some competation activities ---- pow mine
        newBlock.hash, newBlock.proof = self.pow.mine(newBlock.getDataForHash())

        self.chain.append(newBlock)

    # Validation
    def validateChain(self):
        ## If the length of chain is 1
        if (len(self.chain) == 1):
            ### Validate the genesisblock
            if self.chain[0].validateBlock():
                return True
            else:
                return False
        ## When the length of chian is larger than 1
        else:
            for i in range(1,len(self.chain)):
                ### do block validation and check the continous of blocks
                if self.chain[i].validateBlock():
                    if self.chain[i].previousHash == self.chain[i-1].hash:
                        return True
                    else:
                        print("The chain is broken")
                        return False

    def addTransactionToPool(self,transaction):
        if transaction.validateSignature():
            self.transactionPool.append(transaction)
        else:
            raise Exception("invalid transaction")

    def mineBlock(self,minerAddress):
        # 设定矿工奖励transaction
        minerRewardTransaction = Transaction("y3w",minerAddress,self.minerReward)

        # 验证所有的transaction
        for each in self.transactionPool:
            print(each)
            if not each.validateSignature():
                raise Exception("invalid transaction found")

        # Allocate Transaction to Block
        self.allocateTransactions()
        self.allocatedTransactions.insert(0, minerRewardTransaction)
        # 挖矿
        print(self.chain[-1])
        newBlock = Block(self.allocatedTransactions, self.chain[-1].hash)
        newBlock.hash,newBlock.proof = self.pow.mine(newBlock.getDataForHash())
        # 添加区块到区块链
        self.chain.append(newBlock)
        self.allocatedTransactions = []