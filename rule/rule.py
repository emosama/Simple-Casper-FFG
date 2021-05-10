'''
TODO: 未完成（中）
1. fork choose rule
选择哪一条链，规则：选择justified checkpoint最高的链
    -- 在正确的链上，head就是最近的一个BLOCK
    -- 找到justified checkpoint最高的链的descendant < -- update current height to highest
'''
'''
description: stay on the chain with the highest justified checkpoint.
            if we are on the right chain, the head is the latest block
            otherwise find the highest descendant of the highest justified checkpoint
parameters: block: obj, validator: obj
return: head: block
'''
def forkChooseRule(miner, block):
    if miner.checkpoint_set[block.hash].hash == miner.highest_justified_checkpoint.hash:
        return block
    else:
        max_height = miner.highest_justified_checkpoint.height
        max_descendants_hash = miner.highest_justified_checkpoint.hash
        descendants = list(miner.checkpoint_set.keys()).copy()
        for des_hash in descendants:
            if miner.highest_justified_checkpoint.hash == des_hash:
                height = miner.block_set[des_hash].height
                if height > max_height:
                    max_height = height
                    max_descendants_hash = des_hash
        return miner.block_set[max_descendants_hash]

'''
TODO:
2. invalidator detect
   ---- h(t1)  ==  h(t2) 对同一高度的两个target都投票
   ---- h(s1) < h(s2) < h(t2) < h(t1) 投票发生了包含关系
'''
'''
description: invalidator detection. (slashing condition)
parameters: validator: obj, new_votes: set
return: Boolean
'''
def invalidatorDetect(vote_history, new_votes):

    for prev_vote in vote_history:
        if prev_vote["target_epoch"] == new_votes["target_epoch"]:
            return False
        if ((prev_vote["source_epoch"] < new_votes["source_epoch"] and prev_vote["target_epoch"] > new_votes["target_epoch"]) or
            (prev_vote["source_epoch"] > new_votes["source_epoch"] and prev_vote["target_epoch"] < new_votes["target_epoch"])):
            return False
    return True