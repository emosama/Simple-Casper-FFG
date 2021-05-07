logs = {
    "invalidate_vote": []
}


def record_invalidate_vote(log):
    logs["invalidate_vote"].append(log)

def record_invalidate_block(log):
    logs["invalidate_block"].append(log)
