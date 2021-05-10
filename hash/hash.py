import hashlib

def computeHash(information):
    return str(hashlib.sha256((information.encode('utf-8'))).hexdigest())