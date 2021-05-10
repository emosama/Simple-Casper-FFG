import socket
import time
import threading
import json

"""
Author : Maurice Snoeren <macsnoeren(at)gmail.com>
Version: 0.3 beta (use at your own risk)
Date: 7-5-2020

Python package p2pnet for implementing decentralized peer-to-peer network applications
"""


class NodeConnection(threading.Thread):
    """The class NodeConnection is used by the class Node and represent the TCP/IP socket connection with another node. 
       Both inbound (nodes that connect with the server) and outbound (nodes that are connected to) are represented by
       this class. The class contains the client socket and hold the id information of the connecting node. Communication
       is done by this class. When a connecting node sends a message, the message is relayed to the main node (that created
       this NodeConnection in the first place).

       Instantiates a new NodeConnection. Do not forget to start the thread. All TCP/IP communication is handled by this
       connection.
        main_node: The Node class that received a connection.
        sock: The socket that is assiociated with the client connection.
        id: The id of the connected node (at the other side of the TCP/IP connection).
        host: The host/ip of the main node.
        port: The port of the server of the main node."""

    def __init__(self, character, main_node, sock, id, host, port):
        """Instantiates a new NodeConnection. Do not forget to start the thread. All TCP/IP communication is handled by this connection.
            main_node: The Node class that received a connection.
            sock: The socket that is assiociated with the client connection.
            id: The id of the connected node (at the other side of the TCP/IP connection).
            host: The host/ip of the main node.
            port: The port of the server of the main node."""

        super(NodeConnection, self).__init__()

        self.receive_transactions = []

        self.character = character

        self.host = host
        self.port = port
        self.main_node = main_node
        self.sock = sock
        self.terminate_flag = threading.Event()

        # The id of the connected node
        self.id = id

        # End of transmission character for the network streaming messages.
        self.EOT_CHAR = 0x04.to_bytes(1, 'big')

        # Datastore to store additional information concerning the node.
        self.info = {}

        self.main_node.debug_print(
            "NodeConnection.send: Started with client (" + self.id + ") '" + self.host + ":" + str(self.port) + "'")

    '''
    Method description : 
    Input: data : the send data, which can be str,dict or bytes objects.
           encoding_type : using utf-8/ascii to decode the packets ate the other node.
    '''

    def send(self, data, encoding_type='utf-8'):

        if isinstance(data, str):
            self.sock.sendall(data.encode(encoding_type) + self.EOT_CHAR)  # using end of transmission character
        elif isinstance(data, dict):
            try:
                # data is converted to JSON that is send over to the other node
                json_data = json.dumps(data)
                json_data = json_data.encode(encoding_type) + self.EOT_CHAR
                self.sock.sendall(json_data)

            except TypeError as type_error:
                print('This dict is invalid')
            except Exception as e:
                print('Unexpected Error in send message')
        elif isinstance(data, bytes):
            bin_data = data + self.EOT_CHAR
            self.sock.sendall(bin_data)
        else:
            print('datatype used is not valid plese use str, dict (will be send as json) or bytes')

    # This method should be implemented by yourself! We do not know when the message is
    # correct.
    def check_message(self, data):
        return True

    '''Stop the node client. Please make sure you join the thread. '''

    def stop(self):
        self.terminate_flag.set()

    '''
    decode the packet, and return the data
    '''

    def decode_packet(self, packet):
        try:
            packet_decoded = packet.decode('utf-8')
            try:
                return json.loads(packet_decoded)
            except json.decoder.JSONDecodeError:
                return packet_decoded
        except UnicodeDecodeError:
            return packet

    '''
    Required to implement the Thread. This is the main loop of the node client.
    In this method, the thread waits to receive data from another node.
    '''
    def run(self):
        """The main loop of the thread to handle the connection with the node. Within the
           main loop the thread waits to receive data from the node. If data is received 
           the method node_message will be invoked of the main node to be processed."""
        self.sock.settimeout(10.0)
        buffer = b'' # Hold the stream that comes in!

        while not self.terminate_flag.is_set():
            chunk = b''

            try:
                chunk = self.sock.recv(4096)

            except socket.timeout:
                self.main_node.debug_print("NodeConnection: timeout")

            except Exception as e:
                self.terminate_flag.set()
                self.main_node.debug_print('Unexpected error')
                self.main_node.debug_print(e)

            # BUG: possible buffer overflow when no EOT_CHAR is found => Fix by max buffer count or so?
            if chunk != b'':
                buffer += chunk
                eot_pos = buffer.find(self.EOT_CHAR)
                while eot_pos > 0:
                    packet = buffer[:eot_pos]  # 去掉end character
                    buffer = buffer[eot_pos + 1:]
                    data = self.decode_packet(packet)


                    # if data != "" and type(data).__name__ != "dict":
                    #     try:
                    #         data = json.loads(data)
                    #     except:
                    #         print("!!!!!!!!!!!!!!!!!!!")
                    #         print(data)
                    # 去重
                    if data != "" and data != None:
                        # self.main_node.receive_block.append(data)
                        # # 发送给相邻的结点
                        # self.main_node.send_to_nodes(data)
                        # eot_pos = buffer.find(self.EOT_CHAR)

                        # TODO: 判断收到的data是什么类型的
                        #if isinstance(self.miner, Miner):

                        # self.main_node.message_count_recv += 1
                        #
                        # # print("run (receive_data) Method：node_message from " + self.id + ": " + str(data))
                        # # print("")
                        #
                        # self.main_node.receive_block.append(data)
                        # # self.main_node.send_to_nodes(data)
                        # eot_pos = buffer.find(self.EOT_CHAR)

                        if data not in self.main_node.receive_blocks and 'new_block' in data.keys():
                            self.main_node.message_count_recv += 1
                            self.main_node.receive_blocks.append(data)

                            block = json.loads(data["new_block"])
                            self.character.acceptBlock(block)


                        elif data not in self.main_node.receive_votes and 'vote' in data.keys():
                            self.main_node.message_count_recv += 1
                            self.main_node.receive_votes.append(data)
                            vote = json.loads(data["vote"])
                            self.character.validator.acceptVote(vote)

                        elif data not in self.main_node.receive_votes and data not in self.main_node.receive_blocks:
                            print(data)
                        # elif data not in self.main_node.receive_sync and 'sync' in data.keys():
                        #     print("receive sync message")
                        #     self.main_node.receive_sync.append(data)
                        #     highest_justified_checkpoint = json.loads(data["sync"])
                        #     if highest_justified_checkpoint["epoch"] < self.character.highest_justified_checkpoint["epoch"]:
                        #         print("do sync")
                        #         if highest_justified_checkpoint["hash"] in self.character.checkpoint_set:
                        #             if self.character.checkpoint_set[highest_justified_checkpoint["hash"]]["attribute"] != "NORMAL":
                        #                 # 将后续主链发送过去
                        #                 index = self.character.main_chain.index(highest_justified_checkpoint["hash"])
                        #                 for i in range(index, len(self.character.main_chain)):
                        #                     if self.character.main_chain[i] in self.character.checkpoint_set:
                        #                         self.main_node.send_to_node(self, {"checkpoint": self.character.checkpoint_set[self.character.main_chain[i]]})
                        #                     self.main_node.send_to_node(self, {"new_block": self.character.block_set[self.character.main_chain[i]]})
                        #     elif highest_justified_checkpoint["epoch"] > self.character.highest_justified_checkpoint["epoch"]:
                        #         print("reverse sync")
                        #         self.main_node.send_to_node(self, {"sync": self.character.highest_justified_checkpoint, "validator": self.character.user.username})
                        #
                        # elif data not in self.main_node.receive_checkpoint and 'checkpoint' in data.keys():
                        #     self.main_node.receive_checkpoint.append(data)
                        #     checkpoint = json.loads(data["checkpoint"])
                        #     if checkpoint["hash"] not in self.miner.checkpoint_set:
                        #         self.character.checkpoint_set[checkpoint["hash"]] = checkpoint
                        #     else:
                        #         self.character.checkpoint_set[checkpoint["hash"]]["attribute"] = checkpoint["attribute"]
                        #
                        #     if self.character.checkpoint_set[checkpoint["hash"]]["attribute"] == "JUSTIFIED":
                        #         self.character.highest_justified_checkpoint = self.character.checkpoint_set[checkpoint["hash"]]
                        #
                        eot_pos = buffer.find(self.EOT_CHAR)

            time.sleep(0.01)

        # IDEA: Invoke (event) a method in main_node so the user is able to send a bye message to the node before it is closed?

        self.sock.settimeout(None)
        self.sock.close()
        self.main_node.debug_print("NodeConnection: Stopped")

    def set_info(self, key, value):
        self.info[key] = value

    def get_info(self, key):
        return self.info[key]

    def __str__(self):
        return 'NodeConnection: {}:{} <-> {}:{} ({})'.format(self.main_node.host, self.main_node.port, self.host, self.port, self.id)

    def __repr__(self):
        return '<NodeConnection: Node {}:{} <-> Connection {}:{}>'.format(self.main_node.host, self.main_node.port, self.host, self.port)
