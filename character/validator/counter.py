'''
TODO: 未完成（中）
Count votes and store votes history related to specified validator
1. 数vote的数量，判断有没有2/3
2. 记录每一个validator的投票历史
'''
from logs.logs import record_invalidate_vote, logs
import time
from message.vote import Vote
from serialization.serialization import toString
from key.ecdsaKey import generate_ECDSA_keys


class Counter:
    """用于记录投票数量以及所有节点的投票历史
    Attributes:
        count:记录票数，用于进行prepare和commit行为
        voteHistory:记录每个validator的投票记录用于进行invalidate的vote的检测
    """

    def __init__(self):
        """初始化counter
        Args:

        Return:
            无
        """
        self.count = {}  # {source : {target : count} }
        self.vote_history = {}  # {validator_id(the pubkey of specific validator) : [vote](list)}

    def countVote(self, vote, dynasty_size):
        """数票数并判断是否有vote成功通过了2/3

        Args:
            vote: 经过了程式检测，未违反规定的vote
            dynasty_size: dynasty的大小，用于进行‘2/3’判断

        Return:
            无
        """
        # 再次检测vote合法性
        if not vote.validate():
            record_invalidate_vote(("counter.countVote", time.time(), vote))
            return False

        # Vote查重,针对每个validator，每个validator只能提交一个
        if vote.voter_identifier in self.vote_history:
            for each in self.vote_history[vote.voter_identifier]:
                if toString(vote.vote_information) == toString(each):
                    return False

        source = vote.vote_information.source
        target = vote.vote_information.target

        # 初始化self.count[source]为dict
        if source not in self.count:
            self.count[source] = {}
        # 记录count
        self.count[source][target] = self.count[source].get(target, 0) + 1

        if self.count[source][target] > (dynasty_size * 2) // 3: # 提交justified checkpoint以及判断是否提交finalized checkpoint
            return True  # 返回True表明已经到2/3，可以进行‘提交justified checkpoint以及判断是否提交finalized checkpoint’行为了
            print("提交justified checkpoint并判断是否提交finalized checkpoint")
        else:
            return False  # 返回False表明还没到2/3


    def recordVotes(self, vote):
        """记录投票历史

        Args:
            vote: 经过了程式检测，未违反规定的vote

        Return:
            无
        """
        # 再次检测vote合法性
        if not vote.validate():
            record_invalidate_vote(("counter.recordVotes", time.time(), vote))
            return

        # 初始化self.voteHistory[validate_vote.voter_identifier]为list
        if vote.voter_identifier not in self.vote_history:
            self.vote_history[vote.voter_identifier] = []
        # 记录vote_information
        self.vote_history[vote.voter_identifier].append(vote.vote_information)

# # 创建两个密钥对
# p1 = (pubkey, privkey) = generate_ECDSA_keys()
# p2 = (pubkey, privkey) = generate_ECDSA_keys()
#
# # 创建两个vote并签名
# vote1 = Vote("a","b","1","2", p1[0])
# vote1.sign(p2[1])
# vote2 = Vote("a","b","1","2", p2[0])
# vote2.sign(p2[1])
# #创建counter，并进行计数和记录
# counter = Counter(10)
# counter.countVote(vote1)
# counter.recordVotes(vote1)
# counter.countVote(vote2)
# counter.recordVotes(vote2)
#
# print(toString(counter))
# print(logs)