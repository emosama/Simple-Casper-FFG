'''
TODO: 未完成 （优先度低）
Generate user set, miners set and validators set
1. network server
2. 用于规模测试，创建用户集合，矿工集合和验证者集合
'''


from network.MyOwnPeer2PeerNode import MyOwnPeer2PeerNode
from serialization.serialization import toString
import time


node_1 = MyOwnPeer2PeerNode("127.0.0.1", 8001)
node_2 = MyOwnPeer2PeerNode("127.0.0.1", 8002)
node_3 = MyOwnPeer2PeerNode("127.0.0.1", 8003)

time.sleep(1)

node_1.start()
node_2.start()
node_3.start()

time.sleep(1)

node_1.connect_with_node('127.0.0.1', 8002)
node_2.connect_with_node('127.0.0.1', 8001)
node_3.connect_with_node('127.0.0.1', 8002)


Miner_1 = node_1.initialMiner()
newblock = Miner_1.mineBlock(Miner_1.miner_id)
print("the new miner 1 is :")
print(Miner_1.chain)

Miner_2 = node_2.initialMiner()
print("the new miner 2 is :")
print(Miner_2.chain[0].hash)

Miner_3 = node_3.initialMiner()
print("the new miner 3 is :")
print(Miner_3.chain[0].hash)

print("-------")
print(newblock.block_information.previousHash.hash)
print(newblock.hash)
print(toString(newblock))
node_1.send_to_nodes({"new_block": toString(newblock)})

time.sleep(5)
print("------------------------------")
print(node_2.receive_data)


print('end test')