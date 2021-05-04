'''
完成
验证消息合法性
'''
from message.transaction import Transaction
from message.vote import Vote
from tree.block.block import Block
'''
description: 验证消息合法性,vote,transaction,block....
input: msg-->obj
output: True&False
'''
def messageValidation(msg):
    if isinstance(msg, Transaction):
        return msg.validate()
    elif isinstance(msg, Vote):
        return msg.validate()
    elif isinstance(msg, Block):
        return msg.validate()
    else:
        return False