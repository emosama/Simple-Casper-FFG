'''
TODO：修改bcast
矿工
'''

from proposalMechanism.pow import proofOfWork
from key.signature import validateSignature
from configuration.generalParameters import POW_DIFFICULTY
from character.validator.counter import Counter
import threading
import time
import json
from message.message import createTransaction, createBlock, createCheckpoint
from network.MyOwnPeer2PeerNode import MyOwnPeer2PeerNode
from hash.hash import computeHash
from character.validator.validator import Validator
from configuration.generalParameters import EPOCH_TIME


class Miner(threading.Thread):
    def __init__(self, user, host, port):
        super(Miner, self).__init__()
        self.con = threading.Condition()
        self.isStart = -1  # 判断是否挖矿
        self.user = user  # miner的user信息
        # 默认就是validator
        self.node = MyOwnPeer2PeerNode(self, host, port)  # 用于消息传递
        self.node.start()

        self.validator = Validator(self)

        self.block_dependencies = {}

        self.vote_epoch = 0

        root = createBlock("root", None)  # root block
        root["hash"] = computeHash(json.dumps(root["block_information"]))
        root["height"] = 0

        self.block_set = {}  # 树结构 keep the tree of blocks

        self.block_set[root["hash"]] = root  # 存入root block

        self.block_link = {}  # 存储父子关系 父亲--->儿子们

        self.head = root["hash"]  # 当前主链的最高block

        self.pow = proofOfWork(POW_DIFFICULTY)  # pow

        self.transactionPool = []
        # reward to miner a new block
        self.allocatedTransactions = []
        self.minerReward = 50

        # TODO: Right?
        self.preblock_child = {'': [root]}  # {pre block's hash: []}

        # validator相关属性
        ##################
        # 创世block即为创世checkpoint
        # TODO：root checkpoint需要dynasty吗
        # (block_hash, pre_checkpoint_hash, epoch, dynasty)
        self.root_checkpoint = createCheckpoint(root["hash"], None, 0)
        self.root_checkpoint["attribute"] = "JUSTIFIED"
        self.checkpoint_set = {self.root_checkpoint["hash"]: self.root_checkpoint}  # 初始化checkpoint set，记录所有的checkpoint

        self.justified_checkpoints = [self.root_checkpoint["hash"]]
        self.finalized_checkpoints = []
        self.main_chain = [self.root_checkpoint["hash"]]

        self.highest_justified_checkpoint = self.root_checkpoint  # 记录最高的checkpoint

        self.counter = Counter()  # 初始化counter，投票计数以及记录器
        ##################

    def run(self):
        while True:
            if self.isStart == 0:
                self.mineBlock()
            elif self.isStart > 0:
                self.isStart -= 1

    def sync(self):
        self.node.send_to_nodes({"sync": self.highest_justified_checkpoint})

    def acceptBlock(self, block):
        # # 验证block的合法性以及查重
        # # if block.validate() and block.hash not in self.block_set:
        # if block.hash not in self.block_set:
        #     # 记录该block
        #     self.block_set[block.hash] = block
        # # else:
        # #     record_invalidate_block(("validator.acceptBlock", time.time(), block))
        # #     return
        #
        # # 如果block达到了epoch点，则提交vote，并记录checkpoint
        if block["hash"] not in self.block_set:
            # 如果block的父block都还没有接收到
            if block["block_information"]["previous_hash"] not in self.block_set and block["block_information"]["previous_hash"] is not None:
                if block["block_information"]["previous_hash"] not in self.block_dependencies:
                    self.block_dependencies[block["block_information"]["previous_hash"]] = []
                if block not in self.block_dependencies[block["block_information"]["previous_hash"]]:
                    self.block_dependencies[block["block_information"]["previous_hash"]].append(block)
                return block["block_information"]["previous_hash"]

            # 存储block
            self.block_set[block["hash"]] = block
            # 存储父子关系
            if block["block_information"]["previous_hash"] not in self.block_link:
                self.block_link[block["block_information"]["previous_hash"]] = []
            self.block_link[block["block_information"]["previous_hash"]].append(block)

            if block["height"] % EPOCH_TIME == 0:  # and self.vote_epoch < block["height"] / EPOCH_TIME
                previous_checkpoint_hash = self.findNearestCheckpoint(block)
                checkpoint = createCheckpoint(block["hash"], previous_checkpoint_hash, (block["height"] / EPOCH_TIME))
                # 记录该checkpoint
                self.checkpoint_set[checkpoint["hash"]] = checkpoint
                # 如果是validator判断是否投票
                # if self.validator is not None and self.vote_epoch < (block["height"] / EPOCH_TIME):
                if self.validator is not None and self.vote_epoch < checkpoint["epoch"]:
                    self.vote_epoch += 1  # block["height"] / EPOCH_TIME
                    self.validator.generateVote(checkpoint)
                    # 发起投票
            # else:
            #     print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

            self.forkChooseRule(block)

            # 处理voter_dependencies
            if block["hash"] in self.validator.vote_dependencies:
                d_votes = self.validator.vote_dependencies.pop(block["hash"])
                for d_vote in d_votes:
                    self.validator.acceptVote(d_vote)

            # 处理block_dependencies
            if block["hash"] in self.block_dependencies:
                d_blocks = self.block_dependencies.pop(block["hash"])
                for d_block in d_blocks:
                    self.acceptBlock(d_block)
        return None

    def findNearestCheckpoint(self, block):
        previous_block_hash = block["block_information"]["previous_hash"]
        previous_block = self.block_set[previous_block_hash]

        while previous_block["height"] % EPOCH_TIME != 0:
            previous_block = self.block_set[previous_block["block_information"]["previous_hash"]]

        return previous_block["hash"]

    def startMine(self):
        self.pow.startMatch()
        self.isStart = 0

    def stopMine(self):
        self.isStart += 1
        self.pow.stopMatch()

    # 暂定每个block最多10个transaction
    def allocateTransactions(self):
        while len(self.transactionPool) > 0 and len(self.allocatedTransactions) < 10:
            transaction = self.transactionPool.pop(0)
            self.allocatedTransactions.append(transaction)

    def mineBlock(self):
        # 检查head是否在最高Justified checkpoint上
        if not self.isAncestor(self.highest_justified_checkpoint["hash"], self.head):
            print("wrong head")
            self.resetHead()

        # 设定矿工奖励transaction
        reward_transaction = createTransaction("y3w", self.user.username, self.minerReward)

        # 验证所有的transaction
        for transaction in self.transactionPool:
            if not validateSignature(transaction["transaction_information"]["sender"], transaction["signature"],
                                     json.dumps(transaction["transaction_information"])):
                raise Exception("invalid transaction found")

        # Allocate Transaction to Block
        self.allocateTransactions()
        self.allocatedTransactions.insert(0, reward_transaction)

        # 生成一个block
        new_block = createBlock(self.allocatedTransactions, self.head)
        # Set height
        new_block["height"] = (self.block_set[self.head]["height"] + 1)
        # 挖矿
        new_block["hash"], new_block["block_information"]["proof"] = self.pow.mine(new_block["block_information"])

        if new_block["hash"] == None or new_block["block_information"]["proof"] == None:
            print(self.user.username + " Stop mine!!!!!!!!!!!!!!!!!!!")
            # 清空任务表
            self.allocatedTransactions = []
            return
        else:
            # Set timestamp
            new_block["timestamp"] = time.time()

            print(
                str(new_block["height"]) + " " + "Miner: " + self.user.username + "Mine end: " + json.dumps(new_block))

            if new_block["hash"] not in self.block_set:
                self.allocatedTransactions = []
                # 自身接收新的block
                self.acceptBlock(new_block)
                # broadcast to all miner and validator,there is a new block
                self.node.send_to_nodes({"new_block": json.dumps(new_block)})
            # # 挖出新的块，添加区块到区块链
            # if new_block["hash"] not in self.block_set:
            #     # 添加区块到区块链
            #     self.block_set[new_block["hash"]] = new_block
            #
            #     # 添加父子关系 父亲--->儿子们
            #     if new_block["block_information"]["previous_hash"] not in self.block_link:
            #         self.block_link[new_block["block_information"]["previous_hash"]] = []
            #     self.block_link[new_block["block_information"]["previous_hash"]].append(new_block["hash"])
            #
            #     # 重新设置head 根据fork rule
            #     if new_block["height"] > self.block_set[self.head]["height"] and new_block["hash"] != None:
            #         self.head = new_block["hash"]
            #     #
            #     # if self.isAncestor(self.highest_justified_checkpoint["hash"], self.head["hash"]):
            #     #     self.head = new_block["hash"]
            #
            #     self.addChildToPrehash(new_block)

    def addChildToPrehash(self, block):
        # 查到了其有prehash已经有了child
        child_list = []
        if self.preblock_child.get(block["block_information"]["previous_hash"], 0) != 0:
            child_list = self.preblock_child.get(block["block_information"]["previous_hash"], 0)
        child_list.append(block)
        self.preblock_child.update({block["block_information"]["previous_hash"]: child_list})

    # reset head when detect its not on the chain of highest justified checkpoint
    def resetHead(self):
        print("reset head")
        all_peaks = self.findPeaks(self.highest_justified_checkpoint)
        if len(all_peaks) == 0:
            self.head = self.highest_justified_checkpoint["hash"]
        else:
            _head = all_peaks[0]
            for i in range(len(all_peaks)):
                if all_peaks[i]["height"] > _head["height"]:
                    _head = all_peaks[i]
            self.head = _head["hash"]

    # reset head when receive new block
    def forkChooseRule(self, new_block):
        if self.isAncestor(self.highest_justified_checkpoint["hash"], new_block["hash"]):
            if str(self.head) == str(new_block["block_information"]["previous_hash"]):
                self.stopMine()
                self.head = new_block["hash"]
        else:
            self.stopMine()
            self.resetHead()

    def findPeaks(self, block):
        all_peak = []
        if block["hash"] in self.block_link:
            children = self.block_link[block["hash"]]
            for child in children:
                all_peak += self.findPeaks(child)
        return all_peak

    def isAncestor(self, anc_hash, desc_hash):
        if anc_hash == desc_hash:
            return True
        anc = self.block_set[anc_hash]
        desc = self.block_set[desc_hash]

        # 得到desc的父亲的hash
        desc_anc_hash = desc["block_information"]["previous_hash"]
        while desc_anc_hash in self.block_set and desc_anc_hash is not None and desc_anc_hash != "":
            desc_anc = self.block_set[desc_anc_hash]
            if desc_anc["hash"] == anc["hash"]:
                return True
            elif desc_anc["height"] <= anc["height"]:
                return False
            # 一直往前找
            desc_anc_hash = self.block_set[desc_anc["block_information"]["previous_hash"]]["hash"]
        return False

    def joinDynasty(self):
        # request for join
        self.node.send_to_nodes({"join_request": self.user.username})


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
