#!/bin/python3 
import sys
import time
import threading
import queue
import json

otherAppID = sys.argv[1]
appID = sys.argv[2]


class Message:
    def __init__(self, who, what):
        self.who = who  # A qui
        self.what = what  # contenu

    def __str__(self):
        return json.dumps({
            "who": self.who,
            "what": self.what
        })


def MessageFromJson(s):
    d = json.loads(s)
    return Message(d["who"], d["what"])


def lecture(q):
    for line in sys.stdin:
        q.put(MessageFromJson(line))


def ecriture(q, lThread):  # écrire message périodique sur stdout
    while lThread.is_alive():
        q.put(Message(otherAppID, "test"))
        time.sleep(2)


# arrivée d'un message => ajouter événement message en tête de file
# travail à faire => ajouter événement travail en tête de file
def centurion(q, lThread, eThread):
    while not (q.empty()) or (lThread.is_alive() and eThread.is_alive()):
        # lire événement en tête de file /* lecture bloquante */
        message = q.get()
        if message.who == appID:
            print(message.what, file=sys.stderr, flush=True)
        else:
            print(message, file=sys.stdout, flush=True)


if __name__ == "__main__":
    evts = queue.Queue(maxsize=0)
    lectureThread = threading.Thread(target=lecture, args=(evts,))
    ecritureThread = threading.Thread(target=ecriture, args=(evts, lectureThread))
    c = threading.Thread(target=centurion, args=(evts, lectureThread, ecritureThread))
    lectureThread.start()
    ecritureThread.start()
    c.start()
    lectureThread.join()
    ecritureThread.join()
    c.join()
