from serialization.serialization import toString
from key.ecdsaKey import generate_ECDSA_keys
import time
from character.user import User
from character.miner import Miner
import threading

def runMiner(ip_address, port):
    publickey, private_key = generate_ECDSA_keys()
    user = User(publickey, private_key)

    miner = Miner(user, ip_address, port)
    miner.start()

    thread = threading.Thread(target=miner.mineBlock)
    thread.start()

    return miner