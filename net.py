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
    EtatMessage,
    SnapshotRequestMessage
)

appID = sys.argv[1]
nbSite = 3

""" Class
    Net
    
    attribute: 
        - netID: ID of the netSite,
        - nbSite: number of Site in the netword
        - color: color of the netSite (white, red)
        - initiatorSave: is this netSite the initiator 
        - messageAssess: Balance sheet of message in traffic,
        - globalState : global state of the network, according to this netSite
        - nbWaitingMessage: number of waiting message for this netSite
        - nbWaitingState: number of waiting state for this netSite
"""

class Net:
    def __init__(self, netID, nbSite):
        self.netID = netID
        self.nbSite = nbSite
        self.color = "blanc"
        self.initiatorSave = False
        self.messageAssess = 0
        self.etatGlobal = list()
        self.nbMessageAttendu = 0
        self.nbEtatAttendu = 0
        self.messages = queue.Queue(maxsize=0)
        self.lectureThread = threading.Thread(target=self.lecture)
        self.c = threading.Thread(target=self.centurion)
        self.etat = State(self.netID, self.nbSite, self.messageAssess)

    def logger(self, s):
        print(f"From site {self.netID}: {s}", file=sys.stderr, flush=True)
        
    def lecture(self):
        try:
            for line in sys.stdin:
                if line != "\n":
                    m = Message.fromString(line)
                    self.messages.put(("traiter", m))
        except IOError:
            self.logger("Fin de stdin")

    def ecriture(self, message):  # écrire message sur stdout
        self.messages.put(("ecrire", message))

    def centurion(self):
        while not(self.messages.empty()) or self.lectureThread.is_alive():
            # lire événement en tête de file /* lecture bloquante */
            item = self.messages.get()
            if item[0] == "ecrire":
                self.logger(f"Le centurion diffuse le message {item[1]} sur l'anneau")
                print(item[1], file=sys.stdout, flush=True)
            elif item[0] == "traiter":
                message = item[1]
                if str(message.who) == str(self.netID):
                    self.logger(f"Le centurion traite le message {item[1]}")
                    self.receptionMessageExterieur(message)
                elif str(message.who) == "ALL" and str(message.fromWho) != str(self.netID):
                    self.logger(f"Le centurion traite et diffuse le message {item[1]} sur l'anneau")
                    print(message, file=sys.stdout, flush=True)
                    self.receptionMessageExterieur(message)
                else:
                    self.logger(f"Le centurion diffuse le message {item[1]} sur l'anneau")
                    print(message, file=sys.stdout, flush=True)

    def initSauvegarde(self):
        self.logger("Initialisation de la sauvegarde")
        self.color = "rouge"
        self.initiatorSave = True
        self.etatGlobal.append(copy.deepcopy(self.etat))
        self.nbEtatAttendu = self.nbSite - 1
        self.nbMessageAttendu = self.messageAssess
        request = SnapshotRequestMessage(self.netID, self.etat.vectClock)
        request.setColor("rouge")
        self.ecriture(request)

    def envoiMessageDeBase(self, message):
        print("Envoi message provenant de base", file=sys.stderr, flush=True)
        message.setcolor(self.color)
        self.messageAssess += 1
        self.ecriture(message)

    def envoiABase(self, message):
        self.logger(f"{self.netID} envoie {message} à BASE")

    def receptionMessageExterieur(self, m):
        self.etat.vectClock.incr(m.vectClock)
        if m.messageType == "EtatMessage":
            self.logger("Réception message extérieur ETAT")
            if self.initiatorSave:
                etatDistant = State.fromString(m.what)
                self.etatGlobal.append(etatDistant)
                self.nbEtatAttendu -= 1
                self.nbMessageAttendu += etatDistant.messageAssess
                if self.nbMessageAttendu == 0 and self.nbEtatAttendu == 0:
                    self.logger("terminaison de la sauvegarde")
                    with open("save.txt", "w") as fic:
                        for etat in self.etatGlobal:
                            fic.write(str(etat) + "\n")
                    exit(0)
            # else:
            #     print("réception d'un message état mais on est pas initiateur, renvoie", file=sys.stderr, flush=True)
            #     self.ecriture(m)
        elif m.isPrepost:
            self.logger("Réception message extérieur PREPOST")
            if self.initiatorSave:
                self.nbMessageAttendu -= 1
                self.logger(m.contenu)
                self.etatGlobal.extend(m)
                if self.nbMessageAttendu == 0 and self.nbEtatAttendu == 0:
                    self.logger("terminaison de la sauvegarde")
                    with open("save.txt", "w") as fic:
                        for etat in self.etatGlobal:
                            fic.write(str(etat) + "\n")
                    exit(0)
            else:
                self.logger("réception d'un message prepost mais on est pas initiateur, renvoie")
                self.ecriture(m)
        else:
            self.logger("Réception message extérieur NORMAL")
            # TODO, Faire la réception de message
            self.messageAssess -= 1
            if m.color == "rouge" and self.color == "blanc":
                self.logger("Passage en mode sauvegarde")
                self.color = "rouge"
                self.etatGlobal.append(self.etat)
                self.ecriture(EtatMessage(self.netID, self.etat.vectClock, self.etat))    
            if m.color == "blanc" and self.color == "rouge":
                self.logger("Passage au Prepost")
                self.ecriture(m.toPrepost())
  
    def run(self):
        self.lectureThread.start()
        self.c.start()
        self.lectureThread.join()
        self.c.join()


if __name__ == "__main__":
    net = Net(appID, nbSite)
    if int(appID) == 2:
        net.initSauvegarde()
    net.run()
