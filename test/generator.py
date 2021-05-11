'''
TODO: 未完成 （优先度低）
Generate user set, miners set and validators set
1. network server
2. 用于规模测试，创建用户集合，矿工集合和验证者集合
'''

from key.ecdsaKey import generate_ECDSA_keys
from character.user import User
from character.miner import Miner
from flask import Flask, jsonify
from configuration.generalParameters import INIT_DYNASTY

# 初始化miner
miner_size = 6
miners = []  # miner
ip_address = "127.0.0.1"
port_start = 8000
for i in range(miner_size):
    publickey, private_key = generate_ECDSA_keys()
    user = User(publickey, private_key)
    INIT_DYNASTY.append(user.username)
    miner = Miner(user, ip_address, port_start + i)
    miner.start()
    miners.append(miner)
print("-------------------------------------------------")


def complete_connect(miners):
    for i in range(0, len(miners)):
        for j in range(0, len(miners)):
            connect_host = miners[j].node.host
            connect_port = miners[j].node.port
            miners[i].node.connect_node(connect_host, connect_port)


# connect with other miner node
complete_connect(miners)
# for i in range(len(miners)):
#     if i < len(miners) - 1:
#         miners[i].node.connect_node(ip_address, port_start + i + 1)
#     else:
#         miners[i].node.connect_node(ip_address, port_start)

for each in miners:
    each.startMine()

app = Flask(__name__, static_url_path="")


@app.route('/blocks', methods=['GET'])
def get_blocks():
    sets = {}
    for each in miners:
        sets[each.user.username] = each.block_set
    response = {
        'miners': sets
    }
    return jsonify(response), 200


@app.route('/receive', methods=['GET'])
def get_receives():
    sets = {}
    for _miner in miners:
        sets[_miner.user.username] = {
            "receive_blocks": len(_miner.node.receive_blocks),
            "receive_votes": len(_miner.node.receive_votes)
        }
    response = {
        'miners': sets
    }
    return jsonify(response), 200


@app.route('/all_ndoes', methods=['GET'])
def get_all_ndoes():
    sets = {}
    for each in miners:
        sets[each.user.username] = (each.node.message_count_recv, str(each.node.all_nodes()))
    response = {
        'miners': sets
    }
    return jsonify(response), 200


@app.route('/heads', methods=['GET'])
def get_heads():
    sets = {}
    for each in miners:
        sets[each.user.username] = (each.block_set[each.head]["height"], str(each.head),
                                    each.isAncestor(each.highest_justified_checkpoint["hash"], each.head))
    response = {
        'miners': sets
    }
    return jsonify(response), 200


@app.route('/status', methods=['GET'])
def get_status():
    sets = {}
    for each in miners:
        sets[each.user.username] = {"isStart": each.isStart, "continue": each.pow._continue}
    response = {
        'miners': sets
    }
    return jsonify(response), 200


@app.route('/checkpoints', methods=['GET'])
def get_checkpoints():
    sets = {}
    for each in miners:
        sets[each.user.username] = each.checkpoint_set
    response = {
        'miners': sets
    }
    return jsonify(response), 200

@app.route('/blocktree', methods=['GET'])
def get_blocktree():
    sets = {}
    for each in miners:
        sets[each.user.username] = each.block_set
    response = {
        'miners': sets
    }
    return jsonify(response), 200

@app.route('/counts', methods=['GET'])
def get_counts():
    sets = {}
    for each in miners:
        counts = {}
        for source_hash in each.counter.count_forward.keys():
            source = each.checkpoint_set[source_hash]
            source_epoch = source["epoch"]
            if source_epoch not in counts:
                counts[source_epoch] = {}
            counts[source_epoch][source_hash] = each.counter.count_forward[source_hash]
        sets[each.user.username] = counts
    response = {
        'miners': sets
    }
    return jsonify(response), 200


@app.route('/history', methods=['GET'])
def get_history():
    sets = {}
    for a in miners:
        sets[a.user.username] = len(a.counter.vote_history)
    response = {
        'miners': sets
    }
    return jsonify(response), 200


@app.route('/penalty', methods=['GET'])
def get_penalty():
    sets = {}
    for each in miners:
        sets[each.user.username] = each.counter.penalty
    response = {
        'miners': sets
    }
    return jsonify(response), 200


@app.route('/dynasty', methods=['GET'])
def get_dynasty():
    sets = {}
    for each in miners:
        sets[each.user.username] = {
            "current_epoch": each.counter.dynasty.current_epoch,
            "dynasty": each.counter.dynasty.dynasties[each.counter.dynasty.current_epoch]}
    response = {
        'miners': sets
    }
    return jsonify(response), 200


@app.route('/highestJustifiedCheckpoint', methods=['GET'])
def get_highest_justified_checkpoint():
    sets = {}
    for each in miners:
        sets[each.user.username] = each.highest_justified_checkpoint
    response = {
        'miners': sets
    }
    return jsonify(response), 200


@app.route('/checkDependencies1', methods=['GET'])
def checkDependencies1():
    sets = {}
    for each in miners:
        sets[each.user.username] = {
            "vote_J": each.validator.vote_dependencies,
        }
    response = {
        'miners': sets
    }
    return jsonify(response), 200


@app.route('/checkDependencies', methods=['GET'])
def checkDependencies():
    sets = {}
    for each in miners:
        vote_ds = []
        for vote_d in each.validator.vote_dependencies.keys():
            if vote_d in each.checkpoint_set.keys():
                vote_ds.append(1)
            elif vote_d in each.block_set.keys():
                vote_ds.append(2)
            else:
                vote_ds.append(3)
        sets[each.user.username] = {
            "vote_J": vote_ds,
        }
    response = {
        'miners': sets
    }
    return jsonify(response), 200


@app.route('/blockTreeLen', methods=['GET'])
def get_blockTreeLen():
    sets = {}
    for each in miners:
        vote_ds = []
        vote_dd = []
        for vote_d in each.validator.vote_dependencies:
            vote_ds.append((len(each.validator.vote_dependencies[vote_d])))
            vote_dd.append({vote_d: each.validator.vote_dependencies[vote_d]})
        sets[each.user.username] = {
            "vote": len(each.validator.vote_dependencies.keys()),
            "vote_ds": vote_ds,
            "vote_dd": vote_dd,
            "other": (each.counter.call_counter, each.counter.validate_call_counter, len(each.block_set.keys()),
                      len(each.block_dependencies))
        }
    response = {
        'miners': sets
    }
    return jsonify(response), 200

@app.route('/add', methods=['GET'])
def add():
    publickey, private_key = generate_ECDSA_keys()
    user = User(publickey, private_key)
    INIT_DYNASTY.append(user.username)
    miner = Miner(user, ip_address, port_start + len(miners))
    miners.append(miner)
    miner.start()
    complete_connect(miners)
    miner.joinDynasty()
    miner.startMine()

    response = {
        'result': publickey
    }
    return jsonify(response), 200

@app.route('/check_main_chain', methods=['GET'])
def check_main_chain():
    same = True
    length = len(miners)
    for i in range(len(miners[0].main_chain)):
        for j in range(length - 1):
            if miners[j].main_chain[i] != miners[j + 1].main_chain[i]:
                same = False
    sets = {}
    for _miner in miners:
        sets[_miner.user.username] = True
        for i in range(len(_miner.main_chain)):
            if _miner.block_set[_miner.main_chain[i]]["height"] != i:
                height = _miner.block_set[_miner.main_chain[i]]["height"]
                sets[_miner.user.username] = False
            if i > 0:
                if _miner.block_set[_miner.main_chain[i]]["block_information"]["previous_hash"] != _miner.main_chain[
                    i - 1]:
                    sets[_miner.user.username] = False
    response = {
        "same": same,
        'miners': sets,
        "main_chain": miners[0].main_chain
    }
    return jsonify(response), 200

@app.route('/bad_vote', methods=['GET'])
def bad_vote():
    self.validator.generateVote(checkpoint)
    response = {
        "same": same,
        'miners': sets,
        "main_chain": miners[0].main_chain
    }
    return jsonify(response), 200

app.run(host='0.0.0.0', port=5000)
