import socket
import time
import threading
from network.nodeconnection import NodeConnection

"""
Author: Maurice Snoeren <macsnoeren(at)gmail.com>
Version: 0.3 beta (use at your own risk)
Date: 7-5-2020

Python package p2pnet for implementing decentralized peer-to-peer network applications

TODO: Variabele to limit the number of connected nodes.
TODO: Also create events when things go wrong, like a connection with a node has failed.
"""

class Node(threading.Thread):
    """Implements a node that is able to connect to other nodes and is able to accept connections from other nodes.
    After instantiation, the node creates a TCP/IP server with the given port.

    Create instance of a Node. If you want to implement the Node functionality with a callback, you should
    provide a callback method. It is preferred to implement a new node by extending this Node class.
      host: The host name or ip address that is used to bind the TCP/IP server to.
      port: The port number that is used to bind the TCP/IP server to.
      callback: (optional) The callback that is invokes when events happen inside the network
               def node_callback(event, main_node, connected_node, data):
                 event: The event string that has happened.
                 main_node: The main node that is running all the connections with the other nodes.
                 connected_node: Which connected node caused the event.
                 data: The data that is send by the connected node."""

    def __init__(self, character, host, port, callback=None):
        """Create instance of a Node. If you want to implement the Node functionality with a callback, you should
           provide a callback method. It is preferred to implement a new node by extending this Node class.
            host: The host name or ip address that is used to bind the TCP/IP server to.
            port: The port number that is used to bind the TCP/IP server to.
            callback: (optional) The callback that is invokes when events happen inside the network."""
        super(Node, self).__init__()

        self.receive_votes = []
        self.receive_blocks = []
        self.receive_sync = []
        self.receive_checkpoint = []

        self.character = character
        # When this flag is set, the node will stop and close
        self.terminate_flag = threading.Event()

        # Server details, host (or ip) to bind to and the port
        self.host = host
        self.port = port

        # Events are send back to the given callback
        self.callback = callback

        # Nodes that have established a connection with this node
        self.nodes_inbound = []  # Nodes that are connect with us N->(US)->N

        # Nodes that this nodes is connected to
        self.nodes_outbound = []  # Nodes that we are connected to (US)->N

        # Create a unique ID for each node.
        # TODO: A fixed unique ID is required for each node, node some random is created, need to think of it.
        # id = hashlib.sha512()
        # t = self.host + str(self.port) + str(random.randint(1, 99999999))
        # id.update(t.encode('ascii'))
        self.id = self.character.user.username


        # Start the TCP/IP server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()

        # Message counters to make sure everyone is able to track the total messages
        self.message_count_send = 0
        self.message_count_recv = 0
        self.message_count_rerr = 0

        # Debugging on or off!
        self.debug = False

        # self.receive_block = []
        # self.receive_block = []



    '''show all the node in inbound and outbound'''
    def all_nodes(self):
        return self.nodes_inbound + self.nodes_outbound

    def debug_print(self, message):
        """When the debug flag is set to True, all debug messages are printed in the console."""
        if self.debug:
            print("DEBUG: " + message)

    '''Initial the TCP/IP server '''
    def init_server(self):
        print("Initialisation of the Node on port: " + str(self.port) + " on node (" + self.id + ")")
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(None)
        self.sock.listen(5)

    '''check the connection between nodes is still exited'''
    def delete_closed_connections(self):
        for n in self.nodes_inbound:
            if n.terminate_flag.is_set():
                print("inbound_node_disconnected: " + n.id)
                n.join()
                del self.nodes_inbound[self.nodes_inbound.index(n)]

        for n in self.nodes_outbound:
            if n.terminate_flag.is_set():
                print("outbound_node_disconnected: " + n.id)
                n.join()
                del self.nodes_outbound[self.nodes_inbound.index(n)]

    ''' Send a message to all the nodes that are connected with this node.'''
    def send_to_nodes(self, data):
        #to send data for each connection in the inbound and outbound
        for n in (self.nodes_inbound + self.nodes_outbound):
            self.send_to_node(n, data)

    ''' Send the data to the node n '''
    def send_to_node(self, n, data):
        self.message_count_send = self.message_count_send + 1
        self.delete_closed_connections()
        print("send_to_node Method: the n is :" +str(n))
        try:
            n.send(data)
            print("send_to_node Method: finished to send data : "+str(data))
        except Exception as e:
            print("send_to_node Method Error: sending data to the node (" + str(e) + ")")


    '''Connect to target node'''
    def connect_node(self, target_host, target_port):
        # cannot connect to itself
        if target_host == self.host and target_port == self.port:
            print("cannot connect to itself")
            return False
        # the connection is existed
        for node in self.nodes_outbound:
            if node.host == target_host and node.port == target_port:
                print("the connection is existed")
                return True

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target_host, target_port))

        # 交换彼此的id，先发送id，后接受对方的
        sock.send(self.id.encode('utf-8')) # Send my id to the connected node!
        target_node_id = sock.recv(4096).decode('utf-8') # When a node is connected, it sends it id!

        # to create the actual new connection
        node_connection = NodeConnection(self.character, self, sock, target_node_id, target_host, target_port)
        node_connection.start()

        self.nodes_outbound.append(node_connection)
        print("outbound_node_connected: " + self.id)

    '''Disconnect the TCP/IP connection with the specified node.'''
    def disconnect_with_node(self, node):
        if node in self.nodes_outbound:
            # the node from the nodes_outbound list.
            print("node wants to disconnect with oher outbound node: " + node.id)
            node.stop()
            # join the thread, and the application is waiting and waiting
            node.join()
            del self.nodes_outbound[self.nodes_outbound.index(node)]

        else:
            print("Node disconnect_with_node: cannot disconnect with a node with which we are not connected.")

    '''Stop this node and terminate all the connected nodes.'''
    def stop(self):
        print("node is requested to stop!")
        self.terminate_flag.set()




    '''
    The main loop of the thread that deals with connections from other nodes on the network.
    '''
    def run(self):

        # Check whether the thread needs to be closed
        while not self.terminate_flag.is_set():
            try:
                connection, Initiator_address = self.sock.accept()

                # 接收到node的id，发送自己的id
                Initiator_node_id = connection.recv(4096).decode('utf-8')
                connection.send(self.id.encode('utf-8'))
                # to create the actual new connection
                node_connection = NodeConnection(self.character, self, connection, Initiator_node_id, Initiator_address[0],
                                                 Initiator_address[1])
                node_connection.start()

                self.nodes_inbound.append(node_connection)
                print("inbound_node_connected: " + node_connection.id)


            except socket.timeout:
                None
                #print('Node: Connection timeout!')

            # 每0.01s循环一次，监听
            time.sleep(0.01)

        print("Node stopping...")
        for t in self.nodes_inbound:
            t.stop()

        for t in self.nodes_outbound:
            t.stop()

        time.sleep(1)

        for t in self.nodes_inbound:
            t.join()

        for t in self.nodes_outbound:
            t.join()

        self.sock.settimeout(None)
        self.sock.close()
        print("Node stopped")



    def __str__(self):
        return 'Node: {}:{}'.format(self.host, self.port)

    def __repr__(self):
        return '<Node {}:{} id: {}>'.format(self.host, self.port, self.id)
