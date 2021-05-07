'''
已完成
'''
from serialization.serialization import toString
from key.signature import validateSignature, sign
from key.ecdsaKey import generate_ECDSA_keys

class VoteInformation:
    def __init__(self, source, target, epoch_source, epoch_target):
        self.source = source  # source checkpoint hash
        self.target = target  # target checkpoint hash
        self.epoch_source = epoch_source  # source checkpoint height
        self.epoch_target = epoch_target  # target checkpoint height

class Vote:
    # def __init__(self, vote_information, voter_identifier):
    #     self.vote_information = vote_information
    #     self.voter_identifier = voter_identifier # voter的公钥
    #     self.signature = ""

    def __init__(self, source, target, epoch_source, epoch_target, voter_identifier):
        self.vote_information = VoteInformation(source, target, epoch_source, epoch_target)
        self.voter_identifier = voter_identifier # voter的公钥
        self.signature = ""

    def sign(self, privkey):
        self.signature = sign(privkey, toString(self.vote_information))

    def validate(self):
        return validateSignature(self.voter_identifier, self.signature, toString(self.vote_information))

'''
test part ---- for signature(sign&validate) , serialization, message, key-pairs

# generate key
(pubkey, privkey) = generate_ECDSA_keys()

# generate vote
vote = Vote("a","b","1","2", pubkey)

# sign
vote.sign(privkey)

# validation signature
print(vote.validate())

# print serialization result
print(toString(vote))
'''

