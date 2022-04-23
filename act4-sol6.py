#!/bin/python3
import sys
import time
import threading
import queue
import json
from utils import VectClock
from messages import Message, BroadcastMessage, LockRequestMessage, AckMessage, ReleaseMessage, EtatMessage, SnapshotRequestMessage

appID = sys.argv[1]
nbSite = 3


class Etat:
    def __init__(self, netID, N, bilan=0):
        self.bilan = bilan
        self.netID = netID
        tab=[0 for x in range(N)]
        self.vectClock = VectClock(netID, N, tab)

    def __str__(self):
        return f"id = {self.netID}, bilan = {self.bilan}, vectClock = {self.vectClock}"

    def toJSON(self):
        return json.dumps({
            "bilan": self.bilan,
            "netID": self.netID,
            "vectClock": self.vectClock
        })


class Net:
    def __init__(self, netID, nbSite):
        self.netID = netID
        self.nbSite = nbSite
        self.couleur = "blanc"
        self.initiateurSave = False
        self.bilanMessage = 0
        self.etatGlobal = list()
        self.nbMessageAttendu = 0
        self.nbEtatAttendu = 0
        self.messages = queue.Queue(maxsize=0)
        self.lectureThread = threading.Thread(target=self.lecture, args=(self,))
        self.c = threading.Thread(target=self.centurion, args=())
        self.etat = Etat(self.netID, nbSite, self.bilanMessage)

    def lecture(self):
        for line in sys.stdin:
            self.mesages.put(self.messages.fromString(line))

    def ecriture(self, message):  # écrire message sur stdout
        self.messages.put(message)

    def centurion(q, lThread, eThread):
        while not (q.empty()) or (lThread.is_alive() and eThread.is_alive()):
            # lire événement en tête de file /* lecture bloquante */
            message = q.get()
            if message.who == appID:
                print(message.what, file=sys.stderr, flush=True)
            else:
                print(message, file=sys.stdout, flush=True)

    def initSauvegarde(self):
        print("Initialisation de la sauvegarde")
        self.couleur = "rouge"
        self.initiateurSave = True
        self.etatGlobal.append(Etat(self.netID))
        self.nbEtatAttendu = self.nbSite - 1
        self.nbMessageAttendu = self.bilanMessage

    def envoiMessageDeBase(self, message):
        print("Envoi message provenant de base")
        message.setcouleur(self.couleur)
        self.bilanMessage += 1
        self.ecriture(message)

# =============================================================================
#     def envoiMessageExterieur(self, message):
#         print(f"envoie message : {message} depuis {self.netID}")
#         self.ecriture(message)
# =============================================================================

    def envoiABase(self, message):
        print(f"{self.netID} envoie {message} à BASE")

    def receptionMessageExterieur(self, m):
        if m.type == "etat":
            print("Réception message extérieur ETAT")
            if self.initiateurSave:
                etatDistant = json.loads(m.contenu)
                self.etatGlobal.extend(etatDistant)
                self.nbEtatAttendu -= 1
                self.nbMessageAttendu += etatDistant.bilan
                if self.nbMessageAttendu == 0 and self.nbMessageAttendu == 0:
                    print(self.etatGlobal)
                    exit(0)
            else:
                self.envoiMessageExterieur(m)
        elif m.type == "prepost":
            print("Réception message extérieur PREPOST")
            if self.initiateurSave:
                self.nbMessageAttendu -= 1
                print(m.contenu)
                self.etatGlobal.extend(m)
                if self.nbMessageAttendu == 0 and self.nbMessageAttendu == 0:
                    print(self.etatGlobal)
                    exit(0)
            else:
                self.envoiMessageExterieur(m)
        else:
            print("Réception message extérieur NORMAL")
            # TODO, Faire la réception de message
            self.bilanMessage -= 1
            if m.couleur == "rouge" and self.couleur == "blanc":
                self.couleur = "rouge"
                self.etatGlobal.append(Etat(self.bilanMessage, self.netID))
                self.envoiMessageExterieur(EtatMessage(self.netID, self.etat.vectClock, self.etat))    
            if m.couleur == "blanc" and self.couleur == "rouge":
                print("Passage au Prepost")
                self.envoiMessageExterieur(m.toPrepost())
  
    def run(self):
        self.lectureThread.start()
        self.ecritureThread.start()
        self.c.start()
        self.lectureThread.join()
        self.ecritureThread.join()
        self.c.join()

if __name__ == "__main__":
    net = Net(appID, nbSite)
    net.run()
