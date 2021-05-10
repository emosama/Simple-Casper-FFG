'''
TODO: 未完成（难）
包含supermajority link的信息
'''

class supermajorityLink:
    # 传入vote message
    def __init__(self,vote):
        self.source = vote.vote_information.source #checkpoint
        self.target = vote.vote_information.target #checkpoint
        self.source_epoch = vote.vote_information.epoch_source
        self.target_epoch = vote.vote_information.epoch_target

    '''
    update the supermajority link's attributes in the both side
    Input: No arguments
    '''
    def updateLinkNodeAttributes(self):
        if self.source == "JUSTIFIED" or self.source == "FINALIZED":
            # 父节点为justified，则子节点为justified
            self.target.updateAttributes("JUSTIFIED")
            self.target.setSupermajorityLinkSourceHash(self.source)
            # 子节点为justified，则若为父节点的direct child则可以finalized
            if self.target_epoch == self.source_epoch + 1:
                self.source.setAttributes("FINALIZED")



