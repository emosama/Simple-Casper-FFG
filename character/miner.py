'''
TODO：修改bcast
矿工
'''

from proposalMechanism.pow import proofOfWork
from tree.block.block import Block,BlockInformation
from message.transaction import Transaction,TransactionInformation
from serialization.serialization import  toString
# the chain of blockchain
class Miner:
    def __init__(self,public_key, privatekey,difficulty):

        self.chain = [self.bigBang()] #树结构
        self.pow = proofOfWork(difficulty)
        self.transactionPool = []
        #to miner a new block
        self.allocatedTransactions = []
        self.minerReward = 50
        self.miner_id = public_key #公钥
        self.privatekey = privatekey

        #从哪里挖
        self.head = self.chain[-1]
        self.preblock_child={'':[self.chain[0]]} #{pre block's hash: []}


    #生成gensis block
    def bigBang(self):
        print("it is bigbang")
        new_transaction = Transaction(TransactionInformation("y3w", "y3w", "genesis block"))
        genesisBlock = Block(BlockInformation(new_transaction, ''))
        genesisBlock.hash = genesisBlock.computeHash()
        return genesisBlock

    # 暂定每个block最多10个transaction
    def allocateTransactions(self):
        while len(self.transactionPool) > 0 and len(self.allocatedTransactions) < 10:
            transaction = self.transactionPool.pop(0)
            self.allocatedTransactions.append(transaction)


    def get_the_head(self):
        return self.head
    def set_the_head(self,block):
        self.head = block

    # 没用上Add block to chain
    def addBlockToChain(self,newBlock):
        ## Find the hash of the least block
        newBlock.previousHash = self.get_the_head()
        #newBlock.hash = newBlock.computeHash()
        ## Need some competation activities ---- pow mine
        newBlock.hash,newBlock.proof = self.pow.mine(newBlock.getDataForHash())
        self.set_the_head(newBlock)
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
        rewaord_transaction_infor = TransactionInformation("y3w",minerAddress,self.minerReward)
        minerRewardTransaction = Transaction(rewaord_transaction_infor)

        # 验证所有的transaction
        for each in self.transactionPool:
            print(each)
            if not each.validateSignature():
                raise Exception("invalid transaction found")

        # Allocate Transaction to Block
        self.allocateTransactions()
        self.allocatedTransactions.insert(0, minerRewardTransaction)
        # 挖矿
        new_block_info= BlockInformation(self.allocatedTransactions, self.get_the_head())
        newBlock = Block(new_block_info)
        newBlock.hash,newBlock.proof = self.pow.mine(toString(newBlock.block_information))

        # 挖出新的块，添加区块到区块链
        self.chain.append(newBlock)
        self.addChildToPrehash(newBlock)


        self.allocatedTransactions = []

        #TODO:boardcast to all miner and validator,there is a new block
        self.head = newBlock
        return newBlock



    def listening_msd(self,msg,block):
        if msg == 'SEND_NEW_BLOCK':
            self.receNewBlock(block)
        elif msg == 'SEND_NEW_JUSTIFIED':
            self.receJustified(block)


    def receNewBlock(self,rec_block):

        if rec_block.block_information.previousHash == self.head:
            #终止挖掘,添加到chain上,移动head
            self.head = rec_block
        self.chain.append(rec_block)
        self.addChildToPrehash(rec_block)


    def receJustified(self,rec_block):
        #block in the tree
        assert rec_block in self.chain

        self.head = rec_block
        #TODO：完成：移动到tail
        #选择哪一个
        #{pre_hash:block}
        while self.preblock_child.get(block.block_information.previousHash,0) != 0:

            self.head = self.preblock_child[ self.head.block_information.previousHash][0]





    def addChildToPrehash(self,block):
        #查到了其有prehash已经有了child
        child_list =[]
        if self.preblock_child.get(block.block_information.previousHash,0) != 0:
            child_list = self.preblock_child.get(block.block_information.previousHash,0)
        child_list.append(block)
        self.preblock_child.update({block.block_information.previousHash:child_list})


'''
Miner维护一个block tree： block_set = {block.hash:block}

1.miner在head的位置上，挖掘新的block，广播new block给所有的validator和miner

2.miner收到了new block，接受将其添加在自己chain上
    if 该new block的pre block是当前正在挖的block，则终止现在的挖，接受并且，head移动到该block上
    else 则接受将其添加在自己chain上
                    存长
  validator检测block的生成， block到1 epoch的时候发起vote，如果vote通过，则该block为justified
        validator boardcast给all miner 告诉highest justified的值
3.miner收到highest justified的信息之后，更换head的位置于justified的block的子block



'''
