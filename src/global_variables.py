import time
import random
ids_scraped: int = 0
qurantined_tokens = []
locked_tokens = []
blaclisted_users = []


def removeFromQurantine(token):
    time.sleep(630)
    for _i in range(len(qurantined_tokens)):
        if qurantined_tokens[_i] == token:
            qurantined_tokens.pop(_i)


def getGoodToken() -> str:
    while True:
        token = random.choice(open("input/tokens.txt").read().splitlines())
        if (token in qurantined_tokens):
            continue
        if (token in locked_tokens):
            continue
        return token