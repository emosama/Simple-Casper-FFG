'''
TODO: 未完成
Communication network between nodes
方便起见，构建一个集中式的p2p网络，即有一个专门的服务处理所有的communication
包含所有节点，负责所有节点的消息分发
1. time sync
2. broadcast msg

A --> (A.send(server,msg))加入延迟

A ---> (A.send(server,msg)) 没有延迟
server无延时的收到node发给他的信息
server转发给所有的nodes的时候加入延时
'''

from multiprocessing import Process

from character.validator.validator import Validator


def network():
    p = Process(target=Validator.run())
    p.start()




