# general configuration
from enum import Enum

attributes = Enum("attributes",("FINALIZED", "JUSTIFIED", "FAILED", "UNPROCESSED"))

BLOCK_PROPOSAL_TIME = 100
EPOCH_TIME = 5