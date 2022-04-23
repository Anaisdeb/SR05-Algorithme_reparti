import sys
from utils import VectClock

class Message:
    def __init__(self, who, fromWho, messageType, vectClock, what):
        self.who = who
        self.fromWho = fromWho
        self.messageType = messageType
        self.couleur = "blanc"
        self.isPrepost = False
        self.vectClock = vectClock
        self.what = what

    def __str__(self):
        return f"{self.who}~{self.fromWho}~{self.messageType}~{self.couleur}~{self.isPrepost}~{self.vectClock}~{self.what}"

    def toPrepost(self):
        self.isPrepost = True
    
    def setcouleur(self, couleur):
        self.couleur = couleur

    @classmethod
    def fromString(cls, s):
        content = s.split('~')
        print(content, file=sys.stderr, flush=True)
        m = Message(content[0], content[1], content[2], VectClock.from_string(content[5]), content[6])
        m.couleur = content[3]
        if content[4] == "True":
            m.toPrepost()
        return m

class BroadcastMessage(Message):
    def __init__(self, fromWho, messageType, vectClock, what):
        super().__init__("ALL", fromWho, messageType, vectClock, what)

class LockRequestMessage(BroadcastMessage):
    def __init__(self, fromWho, vectClock, stamp):
        super().__init__(fromWho, "LockRequestMessage", vectClock, stamp)

class AckMessage(Message):
    def __init__(self, who, fromWho, vectClock, stamp):
        super().__init__(who, fromWho, "AckMessage", vectClock, stamp)

class ReleaseMessage(BroadcastMessage):
    def __init__(self, fromWho, vectClock, stamp):
        super().__init__(fromWho, "ReleaseMessage", vectClock, stamp)

class EtatMessage(BroadcastMessage):
    def __init__(self, fromWho, vectClock, etat):
        super().__init__(fromWho, "EtatMessage", vectClock, etat)

class SnapshotRequestMessage(BroadcastMessage):
    def __init__(self, fromWho, vectClock):
        super().__init__(fromWho, "SnapshotRequestMessage", vectClock, "This is a snapshot requsupeest!")
