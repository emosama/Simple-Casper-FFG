'''
TODO: 未完成（中）
Count votes and store votes history related to specified validator
1. 数vote的数量，判断有没有2/3
2. 记录每一个validator的投票历史
'''
from rule.dynasty import Dynasty
from rule.rule import invalidatorDetect
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
        # 初始化dynasty
        self.validate_call_counter = 0
        self.call_counter = 0

        self.dynasty = Dynasty()

        self.count_forward = {}  # {source : {target : count} } 对forward validator set进行计数
        self.count_rear = {}  # {source : {target : count} } 对rear validator set进行计数

        self.vote_history = {}  # {validator_id(the pubkey of specific validator) : [vote](list)}

        self.penalty = {}  # 惩罚

    # TODO: 接受加入朝代请求
    # TODO: 接受退出朝代请求

    def countVote(self, vote):
        """数票数并判断是否有vote成功通过了2/3

        Args:
            vote: 经过了程式检测，未违反规定的vote
            dynasty_size: dynasty的大小，用于进行‘2/3’判断

        Return:
            无
        """
        # 再次检测vote合法性
        # if not vote.validate():
        #     record_invalidate_vote(("counter.countVote", time.time(), vote))
        #     return False

        # Vote查重,针对每个validator，每个validator只能提交一个
        # if vote["validator"] in self.vote_history:
        #     for each in self.vote_history[vote["validator"]]:
        #         if (json.dumps(vote["vote_information"])) == json.dumps(each):
        #             return False
        self.call_counter += 1
        if vote["validator"] in self.vote_history:
            if not invalidatorDetect(self.vote_history[vote["validator"]], vote["vote_information"]):
                if vote["validator"] not in self.penalty:
                    self.penalty[vote["validator"]] = []
                self.penalty[vote["validator"]].append((vote))
                print("Penlity!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                return
        self.validate_call_counter += 1
        voter = vote["validator"]
        source = vote["vote_information"]["source_hash"]
        target = vote["vote_information"]["target_hash"]
        current_dynasty = self.dynasty.dynasties[self.dynasty.current_epoch]

        if voter in current_dynasty[0]:
            if source not in self.count_forward:
                self.count_forward[source] = {}
            self.count_forward[source][target] = self.count_forward[source].get(target, 0) + 1

        elif voter in current_dynasty[1]:
            if source not in self.count_forward:
                self.count_forward[source] = {}
            self.count_forward[source][target] = self.count_forward[source].get(target, 0) + 1

            if source not in self.count_rear:
                self.count_rear[source] = {}
            self.count_rear[source][target] = self.count_rear[source].get(target, 0) + 1

        elif voter in current_dynasty[2]:
            if source not in self.count_rear:
                self.count_rear[source] = {}
            self.count_rear[source][target] = self.count_rear[source].get(target, 0) + 1
        else:
            print("invalidate voter")
            return
        self.recordVotes(vote)
        if self.count_forward[source][target] >= ((len(current_dynasty[0]) + len(current_dynasty[1])) * 2) // 3 and self.count_forward[source][target] >= ((len(current_dynasty[2]) + len(current_dynasty[1])) * 2) // 3: # 提交justified checkpoint以及判断是否提交finalized checkpoint
            return True  # 返回True表明已经到rear和forward都满足了2/3，可以进行‘提交justified checkpoint以及判断是否提交finalized checkpoint’行为了
            #print("提交justified checkpoint并判断是否提交finalized checkpoint")
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
        # if not vote.validate():
        #     record_invalidate_vote(("counter.recordVotes", time.time(), vote))
        #     return

        # 初始化self.voteHistory[validate_vote.voter_identifier]为list
        if vote["validator"] not in self.vote_history:
            self.vote_history[vote["validator"]] = []
        # 记录vote_information
        self.vote_history[vote["validator"]].append(vote["vote_information"])

# # 创建两个密钥对
# p1 = (pubkey, privkey) = generate_ECDSA_keys()
# p2 = (pubkey, privkey) = generate_ECDSA_keys()
# p3 = (pubkey, privkey) = generate_ECDSA_keys()
# # 创建两个vote并签名
# vote1 = Vote("a", "b", "1", "2", p1[0])
# vote1.sign(p1[1])
#
# vote2 = Vote("a", "b", "1", "2", p2[0])
# vote2.sign(p2[1])
#
# vote3 = Vote("a", "b", "1", "2", p3[0])
# vote3.sign(p3[1])
#
# INIT_DYNASTY = [p1[0], p2[0], p3[0]]
#
# #创建counter，并进行计数和记录
# counter = Counter()
# print(counter.countVote(vote1))
# counter.recordVotes(vote1)
# print(counter.countVote(vote2))
# counter.recordVotes(vote2)
#
# print(toString(counter))
# print(logs)