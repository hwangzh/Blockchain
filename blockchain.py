#!/usr/bin/python
# -*- coding: utf-8 -*-

# to use sha256 hash for the blockchain
from hashlib import sha256
from block import Block


# The "LinkedList" of the blocks-- a chain of blocks.
class Blockchain():
    # the number of zeros in front of each hash
    difficulty = 4

    # restarts a new blockchain or the existing one upon initialization
    def __init__(self):
        self.chain = []

    # add a new block to the chain
    def add(self, block):
        self.chain.append(block)

    # remove a block from the chain
    def remove(self, block):
        self.chain.remove(block)

    # find the nonce of the block that satisfies the difficulty and add to chain
    def mine(self, block):
        # attempt to get the hash of the previous block.
        # this should raise an IndexError if this is the first block.
        try:
            block.previous_hash = self.chain[-1].hash()
        except IndexError:
            pass

        # loop until nonce that sastisfided difficulty is found
        while True:
            if block.hash()[:self.difficulty] == "0" * self.difficulty:
                self.add(block)
                break
            else:
                # increase the nonce by one and try again
                block.nonce += 1

    # check if blockchain is valid
    def isValid(self):
        # loop through blockchain
        for i in range(1, len(self.chain)):
            _previous = self.chain[i].previous_hash
            _current = self.chain[i - 1].hash()
            # compare the previous hash to the actual hash of the previous block
            if _previous != _current or _current[:self.difficulty] != "0" * self.difficulty:
                return False

        return True


# for testing purposes
def main():
    blockchain = Blockchain()
    database = ["hello", "goodbye", "test", "DATA here"]

    num = 0

    for data in database:
        num += 1
        blockchain.mine(Block(num, data=data))

    for block in blockchain.chain:
        print(block)

    print(blockchain.isValid())

    blockchain.chain[2].data = "NEW DATA"
    blockchain.mine(blockchain.chain[2])
    print(blockchain.isValid())


if __name__ == '__main__':
    main()
