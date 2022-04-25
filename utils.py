import base64

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
    def __init__(
            self,
            netId,
            nbSite,
            clockArray
    ):
        self.netId = int(netId)
        self.nbSite = int(nbSite)
        self.clockArray = clockArray

    def incr(self, otherClock):
        self.clockArray[self.netId] += 1
        for site in range(self.nbSite):
            self.clockArray[site] = max(
                int(self.clockArray[site]),
                int(otherClock.clockArray[site])
            )

    def __str__(self):
        strClockArray = "#".join(map(str, self.clockArray))
        return f"{self.netId}#" \
               f"{self.nbSite}#" \
               f"{strClockArray}"

    @classmethod
    def fromString(cls, stringToConvert):
        clockContent = stringToConvert.split("#")
        return VectClock(
            clockContent[0],
            clockContent[1],
            clockContent[2:]
        )


""" Class
    BasState: class for basSite State

    attribute:
        - text: bas text
        - command: executed command
        - isRequestingCs: state of CS request for this site
        
    method: 
        - __str__(self) --> "encodedtext°command°isRequestingCs"
        - from_string(cls, string) --> get a State from a string (static method)
"""


class BasState:
    def __init__(self, text, command = "", isRequestingCs = False):
        self.text = text
        self.command = command
        self.isRequestingCs = isRequestingCs

    def __str__(self):
        encodedText = base64.b64encode(self.text.encode('utf8')).decode('ascii')
        return f"{self.isRequestingCs}°{self.command}°{encodedText}"

    @classmethod
    def from_string(cls, content):
        isRequestingCs = False
        decodedText = base64.b64decode(content[2].encode('ascii')).decode('utf8')
        if content[0] == "True":
            isRequestingCs = True
        return BasState(content[2], content[1], isRequestingCs)


""" Class
    State: class for netSite State
    
    attribute: 
        - messageAssess: Balance sheet of message in traffic,
        - netId: ID of the netSite,
        - nbSite: number of Site,
        - vectClock: vectorized Clock of the netSite
        - basState: state for bas site
        
    method: 
        - __str__(self) --> "netId°nbSite°messageAssess°vectClock°basState"
        - fromString(cls, string) --> get a State from a string (static method)
"""


class State:
    def __init__(
            self,
            netID,
            nbSite,
            basState,
            messageAssess=0
    ):
        self.messageAssess = int(messageAssess)
        self.netID = int(netID)
        self.nbSite = int(nbSite)
        tab = [0 for x in range(self.nbSite)]
        self.vectClock = VectClock(
            netID,
            nbSite,
            tab
        )
        self.basState = basState

    def __str__(self):
        return f"{self.netID}°" \
               f"{self.nbSite}°" \
               f"{self.messageAssess}°" \
               f"{self.vectClock}°" \
               f"{self.basState}"

    @classmethod
    def fromString(cls, stringToConvert):
        stateContent = stringToConvert.split("°")
        basState = BasState.from_string(stateContent[4:])
        state = State(
            stateContent[0],
            stateContent[1],
            basState,
            stateContent[2]
        )
        state.vectClock = VectClock.fromString(stateContent[3])
        return state
