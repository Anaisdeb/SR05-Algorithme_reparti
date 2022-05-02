#!/bin/python3
import sys
import copy
import threading
import queue
from utils import State
from messages import (
    Message,
    BroadcastMessage,
    LockRequestMessage,
    AckMessage,
    ReleaseMessage,
    StateMessage,
    SnapshotRequestMessage,
    SnapshotReleaseMessage
)
from bas import Bas

appID = sys.argv[1]
nbSite = 4

""" Class
    Net: class that represents netSites
    
    attribute: 
        - netID: ID of the netSite,
        - nbSite: number of Site in the netword,
        - bas: bas application
        - stamp: logical Clock for polling algorithm,
        - networkState: array which represent state of the network, for polling algorithm
        - color: color of the netSite (white, red),
        - initiatorSave: is this netSite the initiator, 
        - globalState : global state of the network, according to this netSite,
        - nbWaitingMessage: number of messages waited by this netSite,
        - nbWaitingState: number of states waited by this netSite,
        - messages: Queue containing messages waiting to be processed,
        - readMessageThread: thread that run readMessage(),
        - centurionThread: thread that run centurion(),
        - state: state of the netSite,
"""


class Net:
    def __init__(self, netID, nbSite):
        self.netID = int(netID)
        self.nbSite = nbSite
        self.bas = Bas(self)
        self.stamp = 0
        self.networkState = {}
        for i in range(self.nbSite):
            self.networkState[i] = ('L', 0)
        self.color = "white"
        self.initiatorSave = False
        self.globalState = list()
        self.nbWaitingMessage = 0
        self.nbWaitingState = 0
        self.messages = queue.Queue(maxsize=0)
        self.readMessageThread = threading.Thread(target=self.readMessage)
        self.centurionThread = threading.Thread(target=self.centurion)
        self.state = State(self.netID, self.nbSite, self.bas.state)

    '''
        logger(self, logContent) --> print logContent in stderr with flush option,
    '''

    def logger(self, logContent):
        print(f"From site {self.netID}: {logContent}", file=sys.stderr, flush=True)

    '''
        readMessage(self) --> read lines from stdin and put them into message Queue, in order to be processed, 
    '''

    def readMessage(self):
        try:
            for line in sys.stdin:
                if line != "\n":
                    readMessage = Message.fromString(line.rstrip("\n"))
                    if str(readMessage.fromWho) != str(self.netID):
                        self.messages.put(("process", readMessage))
                    else:
                        # the message has already been received but will not be processed because it has already gone around the ring
                        self.state.messageAssess -= 1
        except IOError:
            self.logger("End of stdin")

    '''
        writeMessage(self, message) --> put message into message Queue, in order to be sent,
    '''

    def writeMessage(self, message):  # écrire message sur stdout
        message.setColor(self.color)
        self.messages.put(("send", message))

    '''
        centurion(self) --> process every message in queue : 
            if "send" --> send message to the next neighbour
            if "process" --> process the message if it concerns this netSite
    '''

    def centurion(self):
        while not (self.messages.empty()) or self.readMessageThread.is_alive():
            item = self.messages.get()
            if item[0] == "send":
                self.logger(f"The centurion spreads {item[1]} on the Ring")
                self.state.messageAssess += 1
                print(item[1], file=sys.stdout, flush=True)
            elif item[0] == "process":
                message = item[1]
                if str(message.who) == str(self.netID):
                    self.logger(f"The centurion processes  {item[1]}")
                    self.state.messageAssess -= 1
                    self.receiveExternalMessage(message)
                elif str(message.who) == "ALL" and str(message.fromWho) != str(self.netID):
                    # if the message concerns the snapshot global state, there is no need to spread it
                    if not(message.isPrepost or message.messageType == "StateMessage"):
                        self.logger(f"The centurion process and spreads {item[1]} on the Ring")
                        # don't change messageAsses since message is processed then send
                        print(message, file=sys.stdout, flush=True)
                    self.receiveExternalMessage(message)
                else:
                    self.logger(f"The centurion spreads {item[1]} on the Ring")
                    # don't change messageAsses since message is not for us
                    print(message, file=sys.stdout, flush=True)

    '''
        initSnapshot(self) --> 
            initialize snapshot on the netSite concerned, and send request to neighbours in the network
    '''

    def initSnapshot(self):
        self.logger("Initialize snapshot")
        self.color = "red"
        self.initiatorSave = True
        self.globalState.append(copy.deepcopy(self.state))
        self.nbWaitingState = self.nbSite - 1
        self.nbWaitingMessage = self.state.messageAssess
        self.logger(
            f"Waiting {self.nbWaitingState} states and {self.nbWaitingMessage} prepost messages before finishing snapshot")
        request = SnapshotRequestMessage(self.netID, self.state.vectClock)
        request.setColor("red")
        self.writeMessage(request)

    '''
        sendMessageFromBas(self, message) --> spread message received from BAS
    '''

    def sendMessageFromBas(self, message):
        self.logger("Send message received from BAS")
        self.writeMessage(message)

    '''
        sendToBas(self, message) --> send message to BAS (TODO)
    '''

    def sendToBas(self, message):
        self.logger(f"{self.netID} send {message} to BAS")
        self.bas.send(message)

    '''
        basCsRequest(self) --> send Critical Section request message to the network
    '''

    def basCsRequest(self):
        self.stamp += 1
        msg = LockRequestMessage(self.netID, self.state.vectClock, self.stamp)
        self.networkState[self.netID] = ('R', self.stamp)
        self.writeMessage(msg)

    '''
        basCsRelease(self) --> send Critical Section release message to the network
    '''

    def basCsRelease(self):
        self.stamp += 1
        msg = ReleaseMessage(self.netID, self.state.vectClock, self.stamp)
        self.networkState[self.netID] = ('L', self.stamp)
        self.writeMessage(msg)

    '''
        checkState(self) --> check if netSite's state allows itself to enter in Critical Section, i.e.
            - Site is requesting for getting Critical Section access,
            - Site's request is the oldest done,
    '''

    def checkState(self):
        siteState = self.networkState[self.netID][0]
        if siteState == 'R':
            oldestCsRequest = min(self.networkState, key=lambda k: self.networkState[k][1])
            if oldestCsRequest == self.netID:
                self.enterCs()

    '''
        enterCs(self) --> Enter into Critical Section, then send release message to the network
    '''

    def enterCs(self):
        self.logger("Entry in the critical section")
        self.sendToBas("CsOk")
        self.basCsRelease()

    '''
        receiveExternalMessage(self, msgReceived) --> receive message from network, and act according to the type
    '''

    def receiveExternalMessage(self, msgReceived):
        self.state.vectClock.incr(msgReceived.vectClock)
        if msgReceived.messageType == "StateMessage":
            self.receiveExternalStateMessage(msgReceived)
        elif msgReceived.messageType == "LockRequestMessage":
            self.receiveExternalLockRequestMessage(msgReceived)
        elif msgReceived.messageType == "ReleaseMessage":
            self.receiveExternalReleaseMessage(msgReceived)
        elif msgReceived.messageType == "AckMessage":
            self.receiveExternalAckMessage(msgReceived)
        elif msgReceived.isPrepost:
            self.receiveExternalPrepostMessage(msgReceived)
        elif msgReceived.messageType == "SnapshotReleaseMessage":
            self.receiveSnapshotReleaseMessage()
        else:
            self.receiveExternalNormalMessage(msgReceived)

    '''
        receiveExternalStateMessage(self, msgReceived) --> if netSite is the initiator of the snapshot, if it's the last remaining message, 
                                                        finish snapshot and write it into a file
                                                        if it's not the initiator, transmit it to next neighbor 
    '''

    def receiveExternalStateMessage(self, msgReceived):
        self.logger("Receive STATE message")
        if self.initiatorSave:
            etatDistant = State.fromString(msgReceived.what)
            self.globalState.append(etatDistant)
            self.nbWaitingState -= 1
            self.nbWaitingMessage += etatDistant.messageAssess
            self.logger(
                f"Waiting {self.nbWaitingState} states and {self.nbWaitingMessage} prepost messages before finishing snapshot")
            if self.nbWaitingMessage == 0 and self.nbWaitingState == 0:
                self.logger("Finishing snapshot")
                with open("save.txt", "w") as fic:
                    for etat in self.globalState:
                        fic.write(str(etat) + "\n")
                self.initiatorSave = False
                release = SnapshotReleaseMessage(self.netID, self.state.vectClock)
                self.writeMessage(release)
        else:
            self.logger("Received STATE message, not initiator, resend it")
            self.writeMessage(msgReceived)

    '''
        receiveExternalLockRequestMessage(self, msgReceived) --> save Request into networkState, send an ACK, then check state of the netSite
    '''

    def receiveExternalLockRequestMessage(self, msgReceived):
        self.logger("Receive LOCK REQUEST message")
        fromWhoStamp = int(msgReceived.what)
        self.stamp = max(self.stamp, fromWhoStamp) + 1
        self.networkState[int(msgReceived.fromWho)] = ('R', fromWhoStamp)
        ackMessage = AckMessage(msgReceived.fromWho, self.netID, self.state.vectClock, self.stamp)
        self.writeMessage(ackMessage)
        self.checkState()

    '''
        receiveExternalReleaseMessage(self, msgReceived) --> release Request in networkState, then check state of the netSite,
    '''

    def receiveExternalReleaseMessage(self, msgReceived):
        self.logger("Receive Release message")
        fromWhoStamp = int(msgReceived.what)
        self.stamp = max(self.stamp, fromWhoStamp) + 1
        self.networkState[int(msgReceived.fromWho)] = ('L', fromWhoStamp)
        self.checkState()

    '''
        receiveExternalAckMessage(self, msgReceived) --> if no Request is registered for this source, save the ACK into networkState, then check state of the netSite
    '''

    def receiveExternalAckMessage(self, msgReceived):
        self.logger("Receive ACK message")
        fromWhoStamp = int(msgReceived.what)
        self.stamp = max(self.stamp, fromWhoStamp) + 1
        if self.networkState[int(msgReceived.fromWho)][0] != 'R':
            self.networkState[int(msgReceived.fromWho)] = ('A', fromWhoStamp)
        self.checkState()

    '''
        receiveExternalPrepostMessage(self, msgReceived) --> normal message with "isPrepost" at True : same as State Message
    '''

    def receiveExternalPrepostMessage(self, msgReceived):
        self.logger("Receive PREPOST message")
        if self.initiatorSave:
            self.nbWaitingMessage -= 1
            self.logger(msgReceived.contenu)
            self.globalState.extend(msgReceived)
            if self.nbWaitingMessage == 0 and self.nbWaitingState == 0:
                self.logger("Finishing snapshot")
                with open("save.txt", "w") as fic:
                    for etat in self.globalState:
                        fic.write(str(etat) + "\n")
                self.initiatorSave = False
                release = SnapshotReleaseMessage(self.netID, self.state.vectClock)
                self.writeMessage(release)
        else:
            self.logger("Received PREPOST message, not initiator, resend it")
            self.writeMessage(msgReceived)


    '''
        receiveExternalNormalMessage(self, msgReceived) --> if message is red and netSite white, turn netSite into red and turn into SNAPSHOT mode,
                                                            if message is white and netsite red, pass into PREPOST mode
    '''

    def receiveExternalNormalMessage(self, msgReceived):
        self.logger("Receive NORMAL message")
        if msgReceived.messageType != "SnapshotRequestMessage":
            self.sendToBas(msgReceived.what)
        if msgReceived.color == "red" and self.color == "white":
            self.logger("Enter into SNAPSHOT mode")
            self.color = "red"
            self.globalState.append(self.state)
            self.writeMessage(StateMessage(self.netID, self.state.vectClock, str(self.state)))
        if msgReceived.color == "white" and self.color == "red":
            self.logger("switch into PREPOST")
            self.writeMessage(msgReceived.toPrepost())

    '''
        reinitializeNetAfterSnapshot(self) --> reinitialize every var linked to Snapshot Algorithm    
    '''

    def reinitializeNetAfterSnapshot(self):
        self.initiatorSave = False
        self.color = "white"
        self.globalState = []
        self.nbWaitingState = 0
        self.nbWaitingMessage = 0

    '''receiveSnapshotReleaseMessage(self, message) --> if initiatorSave == False, 
                                                        reinitialize var linked to snapshot algo and spread the message 
                                                    --> if initiatorSave == True,
                                                        only reinitialize var linked to snapshot algo. 
    '''

    def receiveSnapshotReleaseMessage(self):
        self.reinitializeNetAfterSnapshot()

    '''
        run(self) --> Run every thread initialized in __init__(self)
    '''

    def run(self):
        self.readMessageThread.start()
        self.centurionThread.start()
        self.bas.run()
        self.readMessageThread.join()
        self.centurionThread.join()


if __name__ == "__main__":
    net = Net(appID, nbSite)
    net.run()
