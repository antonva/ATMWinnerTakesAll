#!/usr/bin/env python3

import sys
import json
import subprocess
import random

gameaddress = "BSJ5jm3jf4Wj5TmLAbzZ2wvHJhwiZmLNdU"
poolsize = 3

def pickwinner(l):
    return random.choice(l)

def pay(winner, amt):
    print(f"paying {winner} {amt} smly")
    subprocess.run(["smileycoin-cli", "sendtoaddress", winner, amt])

def getaddressfromtransaction(txid):
    amttopool = 0
    senderaddress = ""

    cp = subprocess.run(["smileycoin-cli", "getrawtransaction", txid], capture_output=True)
    rawtxid = cp.stdout.decode("utf-8").strip()
    cp = subprocess.run(["smileycoin-cli", "decoderawtransaction", rawtxid], capture_output=True)
    j = json.loads(cp.stdout.decode("utf-8"))

    # Get an address from the first vin
    fa = j["vin"][0]
    cp = subprocess.run(["smileycoin-cli", "getrawtransaction", fa["txid"]], capture_output=True)
    farawtxid = cp.stdout.decode("utf-8").strip()
    cp = subprocess.run(["smileycoin-cli", "decoderawtransaction", farawtxid], capture_output=True)
    faj = json.loads(cp.stdout.decode("utf-8"))
    for vo in faj["vout"]:
        if vo["n"] == fa["vout"]:
            senderaddress = vo["scriptPubKey"]["addresses"][0]

    for vo in j["vout"]:
        # Only handles simple transactions
        if vo["scriptPubKey"]["addresses"][0] == gameaddress:
            amttopool = vo["value"]

    return (senderaddress, amttopool)


def main():
    add, amt = getaddressfromtransaction(sys.argv[1])

    if amt > 0:
        # Load the existing pool
        poolfile = "/home/enoch/.smileycoin/poolfile"
        f = open(poolfile, "r+")
        contestants = json.load(f)
        f.close()
        contestants["pool"] += amt
        contestants["list"].append(add)

        if len(contestants["list"]) >= poolsize:
            winner = pickwinner(contestants["list"])
            pay(winner, contestants["pool"])
            contestants["pool"] = 0
            contestants["list"] = []

        f = open(poolfile, "w")
        json.dump(contestants, f)
        f.close()


if __name__ == "__main__":
    main()
