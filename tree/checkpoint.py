'''
TODO: 未完成（中）
checkpoint
'''
import hashlib
from serialization.serialization import toString


class CheckPoint:
    '''
    Constructor
    A CheckPoint contains the following arguments:
    self.block: the current checkpoint's block
    self.dynasty: the set of validator for current checkpoint
    self.previous_checkpoint_hash: the previous checkpoint's hash
    self.epoch: height of checkpoint

    self.hash: current checkpoint';'s hash
    self.attribute: the checkpoint's state to indicate weather Justified,Finalized or Unprocessed
    self.supermajoritylink_Source: if the current checkpoint is jusified, the source side of supermajority link
                                    if there is no supermajority link, then this attribute is ''

    '''
    #default gensis block， there is no pre checkpoint
    def __init__(self, block):
        self.block = block
        # 拿相应的block作为checkpoint的hash值
        self.hash = block.hash

        #other attributes
        self.dynasty = [] # voters set
        self.previous_checkpoint_hash = ''
        self.pre_blocks = set()
        self.epoch = 0

        self.attribute = "FINALIZED"
        self.supermajoritylink_Source = ''


        # checkpoint_tail is the last block (before the next checkpoint)for the current checkpoint
        checkpoint_tail = block


    #default other checkpoint
    #Input: block:current block,   pre_block；pre checkpoint
    def __init__(self,block, pre_checkpoint,pre_block):

        self.block = block
        self.hash = block.hash

        self.dynasty = [] # voters set
        self.previous_checkpoint_hash = pre_checkpoint.hash
        self.pre_blocks = set()
        self.epoch = pre_checkpoint.epoch + 1


        self.attribute = "UNPROCESSED"
        self.supermajoritylink_Source_hash = ''

    #根据checkpoint的信息计算hash
    def computeHash(self):
        #epoch,preiouse_checkoint_hash,block,    dynasty,
        self.hash = hashlib.sha256((toString(self.block)).encode('utf-8')).hexdigest()
        return str(self.hash)

    '''
    set the attributes
    '''
    def setDynasty(self, dynasty):
        self.dynasty = dynasty
    def setAttributes(self,attribute):
        self.attribute = attribute
    def setSupermajorityLinkSourceHash(self,pre_hash):
        self.supermajoritylink_Source = pre_hash

    def setCheckPointTail(self,block):
        self.checkpoint_tail = block




'''

1.vote的source和target都是一个checkpoint
2.chechpoint的连接是按照block的连接确定的
3.每一个通过2/3的vote，是一个supermajority link
4.supermajority link的两端都是jusitified


提出一个vote，其soure是justified，target是unprocessed的checkpoint
每一次遇到新的checkpoint和其祖先中最近的justified的checkpoint，提出一个vote：
    if vote通过 则这是一个suoermajoritylink，并更新属性
    if没有通过，则为普通的checkpoint之间的连接


#1.一个validator维护一个block tree和checkpoint tree。
#2. tree的结构由一个list维护 回溯


tail_membership
closest_ancestor_checkpoint:指的是每一个block，Closest checkpoint ancestor for each block
checkpoint_tail:Tails are for checkpoint blocks, the tail is the last block
                (before the next checkpoint) following the checkpoint   
               
 
                
#Closest checkpoint ancestor for each block,dic{the block hash,the ancester hash}
closest_ancestor_checkpoint = {self.hash:self.hash}
#checkpoint_tail is the last block (before the next checkpoint)for the current checkpoint
checkpoint_tail ={self.hash:block}







我想说一下关于我那部分，首先先给大家道个歉，



1.选择那一部分，然后我选择了link和checkpoint的部分，
2.我自己在写的过程中也发现，确实这部分可以被其他部分尤其是validator那部分写了，我这里只用实现简单的过程

3.然后我就开始看了network，因为我们也没讨论到。

反正我说的意思就是 虽然是说我这两天写的的东西没有被用上，写的那部分也被缩减没啥用了，但是我不是说在划水
然后我前面确实有些不开心，后面也没有参与讨论，给大家道个歉，
当时就是觉得很委屈，觉得自己明明干了活，觉得还很认真的正在写，结果没用上 可能有些失落。


'''





