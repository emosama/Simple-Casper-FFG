
def createBlock(transactions, previous_hash):
    block = {
        "block_information": {
            "previous_hash": previous_hash,
            "transactions": transactions,
            "proof": None
        },
        "hash": None,
        "height": None,
        "timestamp": None
    }
    return block


def createTransaction(sender, receiver, amount):
    transaction = {
        "transaction_information": {
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        },
        "signature": None
    }
    return transaction

def createCheckpoint(block_hash, pre_checkpoint_hash, epoch):
    checkpoint = {
        "hash" : block_hash,
        "previous_checkpoint_hash": pre_checkpoint_hash,
        "epoch" : epoch,
        "attribute": "NORMAL"
    }
    return checkpoint
    # self.pre_blocks = set()
    # self.supermajoritylink_Source_hash = ''

def createVote(source_hash, target_hash, source_epoch, target_epoch, validator):
    vote = {
        "vote_information":{
            "source_hash": source_hash,
            "target_hash": target_hash,
            "source_epoch": source_epoch,
            "target_epoch": target_epoch
        },
        "validator": validator,
        "signature": None

    }
    return vote