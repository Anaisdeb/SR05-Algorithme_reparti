""" Class
    VectClock : class for vectorized clock

    attribute:
        netID: ID of the Net concerned by the clock
        nbSite: Number of Site in the network
        clockArray: Value of the vectorized clock

    method:
        incr(self, otherClock) --> increment the clock with an other one
        __str__(self) --> "netId#nbSite#clockArray"
        fromString(cls, stringToConvert) --> get VectClock Instance from a String (static method)
"""


class VectClock:
    def __init__(self, netId, nbSite, clockArray):
        self.netId = int(netId)
        self.nbSite = int(nbSite)
        self.clockArray = clockArray

    def incr(self, otherClock):
        self.clockArray[self.netId] += 1
        for site in range(self.nbSite):
            self.clockArray[site] = max(int(self.clockArray[site]), int(otherClock.tab[site]))

    def __str__(self):
        strClockArray = "#".join(map(str, self.clockArray))
        return f"{self.netId}#{self.nbSite}#{strClockArray}"

    @classmethod
    def fromString(cls, stringToConvert):
        clockContent = stringToConvert.split("#")
        return VectClock(clockContent[0], clockContent[1], clockContent[2:])


""" Class
    State: class for netSite State
    
    attribute: 
        - messageAssess: Balance sheet of message in traffic,
        - netId: ID of the netSite,
        - nbSite: number of Site,
        - vectClock: vectorized Clock of the netSite
        
    method: 
        - __str__(self) --> "netId°nbSite°messageAssess°vectClock"
        - fromString(cls, string) --> get a State from a string (static method)
"""


class State:
    def __init__(self, netID, nbSite, messageAssess=0):
        self.messageAssess = int(messageAssess)
        self.netID = int(netID)
        self.nbSite = int(nbSite)
        tab = [0 for x in range(self.nbSite)]
        self.vectClock = VectClock(netID, nbSite, tab)

    def __str__(self):
        return f"{self.netID}°{self.nbSite}°{self.messageAssess}°{self.vectClock}"

    @classmethod
    def fromString(cls, stringToConvert):
        stateContent = stringToConvert.split("°")
        state = State(stateContent[0], stateContent[1], stateContent[2])
        state.vectClock = VectClock.fromString(stateContent[3])
        return state
