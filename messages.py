from utils import VectClock

""" Class
    Message: class for messages transmitted between netSite
    
    attribute: 
        - who: destination of the message,
        - fromWho: source of the message,
        - messageType: type of the message : 
            - LockRequestMessage,
            - AckMessage,
            - ReleaseMessage,
            - StateMessage,
            - SnapshotRequestMessage
        - color: color of the message (and the netSite who send it),
        - isPrepost: is this message a prepost ? 
        - vectClock: vectorized clock of the source of the message (Snapshot Algorithm),
        - what: content of the message
        
    method: 
        - __str__(self) --> "who~fromWho~messageType~color~isPrepost~vectClock~what",
        - toPrepost(self) --> return the same message after switching "toPrepost" to "True",
        - setColor(self, color) --> setter for color attribute,
        - fromString(cls, s) --> get Message instance from a string (static method)
"""


class Message:
    def __init__(
            self,
            who,
            fromWho,
            messageType,
            vectClock,
            what
    ):
        self.who = who
        self.fromWho = fromWho
        self.messageType = messageType
        self.color = "white"
        self.isPrepost = False
        self.vectClock = vectClock
        self.what = what

    def __str__(self):
        return f"{self.who}~" \
               f"{self.fromWho}~" \
               f"{self.messageType}~" \
               f"{self.color}~" \
               f"{self.isPrepost}~" \
               f"{self.vectClock}~" \
               f"{self.what}"

    def toPrepost(self):
        self.isPrepost = True
        return self
    
    def setColor(self, color):
        self.color = color

    @classmethod
    def fromString(cls, s):
        content = s.split('~')
        m = Message(
            content[0],
            content[1],
            content[2],
            VectClock.fromString(content[5]),
            content[6]
        )
        m.color = content[3]
        if content[4] == "True":
            m.toPrepost()
        return m


""" Class 
    Message --> BroadcastMessage : Message with "All" in who attribute
"""


class BroadcastMessage(Message):
    def __init__(self, fromWho, messageType, vectClock, what):
        super().__init__("ALL", fromWho, messageType, vectClock, what)


""" Class
    BroadcastMessage --> EditMessage : Message with "EditMessage" in messageType attribute
"""


class EditMessage(BroadcastMessage):
    def __init__(self, fromWho, vectClock, what):
        super().__init__(fromWho, "EditMessage", vectClock, what)


""" Class 
    BroadcastMessage --> LockRequestMessage : Message with "LockRequestMessage" in type attribute
"""


class LockRequestMessage(BroadcastMessage):
    def __init__(self, fromWho, vectClock, stamp):
        super().__init__(fromWho, "LockRequestMessage", vectClock, stamp)


""" Class 
    Message --> AckMessage : Message with "AckMessage" in type attribute
"""


class AckMessage(Message):
    def __init__(self, who, fromWho, vectClock, stamp):
        super().__init__(who, fromWho, "AckMessage", vectClock, stamp)


""" Class 
    BroadcastMessage --> ReleaseMessage : Message with "ReleaseMessage" in type attribute
"""


class ReleaseMessage(BroadcastMessage):
    def __init__(self, fromWho, vectClock, stamp):
        super().__init__(fromWho, "ReleaseMessage", vectClock, stamp)


""" Class 
    BroadcastMessage --> StateMessage : Message with "StateMessage" in type attribute
"""


class StateMessage(BroadcastMessage):
    def __init__(self, fromWho, vectClock, etat):
        super().__init__(fromWho, "StateMessage", vectClock, etat)


""" Class 
    BroadcastMessage --> SnapshotRequestMessage : Message with "SnapshotRequestMessage" in type attribute,
                         what doesn't matter
"""


class SnapshotRequestMessage(BroadcastMessage):
    def __init__(self, fromWho, vectClock):
        super().__init__(fromWho, "SnapshotRequestMessage", vectClock, "This is a snapshot request!")


''' class linked to  implementation of multiple snapshot 
class SnapshotReleaseMessage(BroadcastMessage):
    def __init__(self, fromWho, vectClock):
        super().__init__(fromWho, "SnapshotReleaseMessage", vectClock, "This is a snapshot release!")
'''