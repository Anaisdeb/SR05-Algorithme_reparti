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

    def lecture(self):
        for line in sys.stdin:
            if line != "\n":
                m = Message.fromString(line)
                if m.fromWho != self.netID:
                    self.messages.put(m)

    def ecriture(self, message):  # écrire message sur stdout
        self.messages.put(message)

    def centurion(self):
        while not(self.messages.empty()) or self.lectureThread.is_alive():
            # lire événement en tête de file /* lecture bloquante */
            message = self.messages.get()
            print(f"Le centurion de {self.netID} de traite {message}", file=sys.stderr, flush=True)
            if str(message.who) == str(self.netID):
                self.receptionMessageExterieur(message)
            elif str(message.who) == "ALL" and str(message.fromWho) != str(self.netID):
                print(message, file=sys.stdout, flush=True)
                self.receptionMessageExterieur(message)
            else:
                print(f"Le centurion diffuse le message sur l'anneau", file=sys.stderr, flush=True)
                print(message, file=sys.stdout, flush=True)

    def initSauvegarde(self):
        print("Initialisation de la sauvegarde", file=sys.stderr, flush=True)
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

# =============================================================================
#     def envoiMessageExterieur(self, message):
#         print(f"envoie message : {message} depuis {self.netID}")
#         self.ecriture(message)
# =============================================================================

    def envoiABase(self, message):
        print(f"{self.netID} envoie {message} à BASE", file=sys.stderr, flush=True)

    def receptionMessageExterieur(self, m):
        self.etat.vectClock.incr(m.vectClock)
        if m.messageType == "EtatMessage":
            print("Réception message extérieur ETAT", file=sys.stderr, flush=True)
            if self.initiatorSave:
                etatDistant = State.fromString(m.what)
                self.etatGlobal.append(etatDistant)
                self.nbEtatAttendu -= 1
                self.nbMessageAttendu += etatDistant.bilan
                if self.nbMessageAttendu == 0 and self.nbEtatAttendu == 0:
                    print("terminaison de la sauvegarde", file=sys.stderr, flush=True)
                    print(self.etatGlobal, file=sys.stderr, flush=True)
                    with open("save.txt", "w") as fic:
                        for etat in self.etatGlobal:
                            fic.write(str(etat) + "\n")
                    exit(0)
            # else:
            #     print("réception d'un message état mais on est pas initiateur, renvoie", file=sys.stderr, flush=True)
            #     self.ecriture(m)
        elif m.isPrepost:
            print("Réception message extérieur PREPOST", file=sys.stderr, flush=True)
            if self.initiatorSave:
                self.nbMessageAttendu -= 1
                print(m.contenu, file=sys.stderr, flush=True)
                self.etatGlobal.extend(m)
                if self.nbMessageAttendu == 0 and self.nbEtatAttendu == 0:
                    print(self.etatGlobal, file=sys.stderr, flush=True)
                    exit(0)
            else:
                print("réception d'un message prepost mais on est pas initiateur, renvoie", file=sys.stderr, flush=True)
                self.envoiMessageExterieur(m)
        else:
            print("Réception message extérieur NORMAL", file=sys.stderr, flush=True)
            # TODO, Faire la réception de message
            print(m, file=sys.stderr, flush=True)
            self.messageAssess -= 1
            if m.color == "rouge" and self.color == "blanc":
                print("Passage en mode sauvegarde", file=sys.stderr, flush=True)
                self.color = "rouge"
                self.etatGlobal.append(self.etat)
                self.ecriture(EtatMessage(self.netID, self.etat.vectClock, self.etat))    
            if m.color == "blanc" and self.color == "rouge":
                print("Passage au Prepost", file=sys.stderr, flush=True)
                self.envoiMessageExterieur(m.toPrepost())
  
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
