'''
已完成
'''
from serialization.serialization import toString
from key.signature import validateSignature, sign
from key.ecdsaKey import generate_ECDSA_keys

class VoteInformation:
    def __init__(self, source, target, epoch_source, epoch_target):
        self.source = source
        self.target = target
        self.epoch_source = epoch_source
        self.epoch_target = epoch_target

class Vote:
    def __init__(self, vote_information, voter_identifier):
        self.vote_information = vote_information
        self.voter_identifier = voter_identifier # voter的公钥
        self.signature = ""

    def sign(self, privkey):
        self.signature = sign(privkey, toString(self.vote_information))

    def validate(self):
        assert validateSignature(self.voter_identifier, self.signature, toString(self.vote_information)), "Invalidate signature"

'''
test part ---- for signature(sign&validate) , serialization, message, key-pairs
'''
# generate key
(pubkey, privkey) = generate_ECDSA_keys()

# generate vote
vote_information = VoteInformation("a","b","1","2")
vote = Vote(vote_information, pubkey)

# sign
vote.sign(privkey)

# validation signature
print(vote.validate())

# print serialization result
print(toString(vote_information))
print(toString(vote))