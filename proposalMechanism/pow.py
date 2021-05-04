'''
已完成
'''
import hashlib

class proofOfWork:
    def __init__(self, difficulty = 1):
        self.difficulty = difficulty

    def changeDifficulty(self,difficulty):
        self.difficulty = difficulty

    def getAnswer(self):
        ## The front n char is 0
        answer = ''
        for i in range(self.difficulty):
            answer += '0'
        return answer

    def computeHash(self,data,noce):
        return str(hashlib.sha256((data + str(noce)).encode('utf-8')).hexdigest())


    # Comput hash according to the difficulty
    def mine(self,data):
        noce = 1
        while(True):
            hash = self.computeHash(data, noce)
            if hash[:self.difficulty] == self.getAnswer():
                print("Mine end: " + hash)

                # TODO: broadcast block

                return hash,noce
            else:
                noce += 1