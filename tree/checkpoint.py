'''
TODO: 未完成（中）
checkpoint
'''
from configuration.generalParameters import attributes # Attributes写到configuration里去了

class checkpoint:
    def __init__(self, blocks):
        self.blocks = blocks
        self.dynasty = [] # voters set
        self.previous_checkpoint_hash = ""
        self.hash = ""
        self.attribute = attributes.UNPROCESSED

    def updateAttributes(self):


