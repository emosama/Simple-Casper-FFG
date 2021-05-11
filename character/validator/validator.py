'''
TODO：未完成
依赖：
'''
from message.message import createCheckpoint,createVote
from key.signature import sign, validateSignature
import json

class Validator():
    """用于构建validator节点

    """
    def __init__(self, miner):
        """
        """
        self.miner = miner
        # TODO：用于保存所有的早产block和vote，然后延后处理他们？
        self.vote_dependencies = {}

        self.vote_history = {}

        self.vote_sync_dependencies ={}


    def acceptVote(self, vote):
        # 如果source或者target没在自己的记录里面呢？
        if vote["vote_information"]["source_hash"] not in self.miner.checkpoint_set:
            if vote["vote_information"]["source_hash"] not in self.vote_dependencies:
                self.vote_dependencies[vote["vote_information"]["source_hash"]] = []
            self.vote_dependencies[vote["vote_information"]["source_hash"]].append(vote)
            # self.miner.node.send_to_nodes({"ask_block": vote["vote_information"]["source_hash"]})
            return vote["vote_information"]["source_hash"]

        if vote["vote_information"]["target_hash"] not in self.miner.checkpoint_set:
            if vote["vote_information"]["target_hash"] not in self.vote_dependencies:
                self.vote_dependencies[vote["vote_information"]["target_hash"]] = []
            self.vote_dependencies[vote["vote_information"]["target_hash"]].append(vote)
            # self.miner.node.send_to_nodes({"ask_block": vote["vote_information"]["target_hash"]})
            return vote["vote_information"]["target_hash"]

        if self.miner.checkpoint_set[vote["vote_information"]["source_hash"]]["attribute"] != "JUSTIFIED":
            if vote["vote_information"]["source_hash"] not in self.vote_sync_dependencies:
                self.vote_sync_dependencies[vote["vote_information"]["source_hash"]] = []
            if vote not in self.vote_sync_dependencies[vote["vote_information"]["source_hash"]]:
                self.vote_sync_dependencies[vote["vote_information"]["source_hash"]].append(vote)
            return None

        # 返回为true时，表明该vote达到了2/3条件，此时进行prepare和commit
        if self.miner.counter.countVote(vote):
            source = self.miner.checkpoint_set[vote["vote_information"]["source_hash"]]
            target = self.miner.checkpoint_set[vote["vote_information"]["target_hash"]]
            # prepare process
            # if source["attribute"] is attributes.JUSTIFIED or source["attribute"] is attributes.FINALIZED:
            if source["attribute"] is "JUSTIFIED":
                target["attribute"] = "JUSTIFIED"
                self.miner.justified_checkpoints.append(target["hash"])

                # 更新main_chain, record blocks from the last justified checkpoint to the nearest justified checkpoint before it.
                chain = []
                chain.append(target["hash"])
                pre_block = self.miner.block_set[target["hash"]]
                while pre_block["hash"] != self.miner.highest_justified_checkpoint["hash"]:
                    chain.append(pre_block["hash"])
                    pre_block = self.miner.block_set[pre_block["block_information"]["previous_hash"]]
                chain.reverse()
                self.miner.main_chain += chain

                # 更新highest justified checkpoint
                self.miner.highest_justified_checkpoint = target

                # 判断同步vote缓存是否有需要执行的
                if target["hash"] in self.vote_sync_dependencies:
                    votes = self.vote_sync_dependencies[target["hash"]]
                    for vote in votes:
                        self.acceptVote(vote)

            # commit process
            # if (target["attribute"] == attributes.JUSTIFIED and source["attribute"] == attributes.JUSTIFIED and target["epoch"] - source["epoch"] == 1) or source["hash"] == self.miner.root_checkpoint["hash"]:
            if source["attribute"] == "JUSTIFIED" and ((target["attribute"] == "JUSTIFIED" and target["epoch"] - source["epoch"] == 1) or source["hash"] == self.miner.root_checkpoint["hash"]):
                source["attribute"] = "FINALIZED"
                self.miner.justified_checkpoints.remove(target["hash"])
                self.miner.finalized_checkpoints.append(source["hash"])
                # Commit后表明有新的finalize出现，这个时候朝代要更替
                self.miner.counter.dynasty.dynastyChange()
        return None

    def generateVote(self, target):
        vote = createVote(self.miner.highest_justified_checkpoint["hash"], target["hash"], self.miner.highest_justified_checkpoint["epoch"], target["epoch"], self.miner.user.username)
        sign(self.miner.user.privkey, json.dumps(vote["vote_information"]))

        self.acceptVote(vote)
        # broadcast vote to other nodes

        # store personal vote history
        self.vote_history[self.miner.vote_epoch] = vote
        self.miner.node.send_to_nodes({"vote": json.dumps(vote)})


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




