'''
TODO：未完成
依赖：
'''
from character.validator.counter import Counter
from configuration.generalParameters import attributes
from message.vote import Vote
from logs.logs import record_invalidate_block, record_invalidate_vote, logs
import time
from  configuration.generalParameters import EPOCH_TIME
from tree.checkpoint import CheckPoint
from tree.block.block import Block

class Validator:
    """用于构建validator节点


    """
    def __init__(self, validator_id, privkey):
        """
        """
        ##### Checkpoint part
        self.validator_id = validator_id  # 其实就是公钥
        self.privkey = privkey  # 私钥
        self.highest_justified_checkpoint = self.root_checkpoint.hash  # 记录最高的checkpoint的hash

        # 创世block
        root_block = Block()
        # 初始化block set，记录所有的block
        self.block_set = {root_block.hash:root_block}  # 记录所有的block

        # 创世block即为创世checkpoint
        # TODO：root checkpoint需要dynasty吗
        root_checkpoint = CheckPoint(root_block.hash, None, 0)
        root_checkpoint.attribute = attributes.JUSTIFIED
        # 初始化checkpoint set，记录所有的checkpoint
        self.checkpoint_set = {root_checkpoint.hash:root_checkpoint }

        # 初始化counter，投票计数以及记录器
        self.counter = Counter()

        # TODO：用于保存所有的早产block和vote，然后延后处理他们？
        self.dependencies = {}


    def acceptBlock(self, block):
        # TODO: 如果block的父block都还没有接收到呢？
        # 验证block的合法性以及查重
        if block.validate() and block.hash not in self.block_set:
            # 记录该block
            self.block_set[block.hash] = block
        else:
            record_invalidate_block(("validator.acceptBlock", time.time(), block))
            return

        # 如果block达到了epoch点，则提交vote，并记录checkpoint
        if block.height % EPOCH_TIME == 0:
            # TODO: 自动生成朝代，待完成
            dynasty = []
            # 创建checkpoint
            epcoh = block.height/EPOCH_TIME
            checkpoint = CheckPoint(block.hash, dynasty, epcoh)
            # 记录该checkpoint
            self.checkpoint_set[block.hash] = checkpoint
            # 发起投票
            self.generateVote(checkpoint, self.privkey)

    def acceptVote(self, vote):
        # TODO: 如果source或者target没在自己的记录里面呢？
        if self.counter.countVote(vote):  # 返回为true时，表明该vote达到了2/3条件，此时进行prepare和commit
            source = self.checkpoint_set[vote.source]
            target = self.checkpoint_set[vote.target]
            # prepare process
            if target.attribute == attributes.JUSTIFIED:
                source.attribute = attributes.JUSTIFIED
                # 更新highest justified checkpoint
                self.highest_justified_checkpoint = source.hash
            # commit process
            if source.attribute == attributes.JUSTIFIED and source.epoch - target.epoch == 1:
                target.attribute = attributes.FINALIZED

    def generateVote(self, target, privkey):
        vote = Vote(self.highest_justified_checkpoint.hash, target.hash, self.highest_justified_checkpoint.epoch, self.target.epoch, self.validator_id)
        vote.sign(privkey)
        if vote.validate():
            # TODO: 发送给network去广播自己的vote
            return
        else:
            # TODO: 报告错误
            record_invalidate_vote(("validator.generateVote", time.time(), vote))

    def addDependency(self):
        return

    # def getPreviousCheckpoint(self, checkpoint):
    #     # 获取当前checkpoint对应的block
    #     block = self.block_set[checkpoint.hash]
    #     # 找到这个block的previous checkpoint，便找到了这个checkpoint的previous checkpoint
    #     return block.previous_checkpoint
    #
    # def getPreviousJustifiedCheckpoint(self, checkpoint):
    #     # 获取当前checkpoint的前一个非checkpoint的block
    #     block = self.block_set[checkpoint.hash]
    #     # 找到这个block的previous checkpoint，便找到了这个checkpoint的previous checkpoint
    #     return block.previous_justified_checkpoint
    #
    # def getChildCheckpoints(self,checkpoint):
    #     return self.checkpoint_tree[checkpoint.hash]
    #
    # def isAncestor(self, anc_hash, desc_hash):
    #     children_hashes = self.checkpoint_tree[anc_hash]
    #     while True:
    #         if children_hashes == None:
    #             return False
    #         elif desc_hash in children_hashes:
    #             return True
    #         else:
    #             for child_hash in children_hashes:
    #                 if self.isAncestor(child_hash, desc_hash):
    #                     return True
    #             return False




