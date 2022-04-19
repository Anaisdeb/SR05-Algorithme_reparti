import json
import copy

NbSite = 3


class Etat:
    def __init__(self, netID, bilan=0):
        self.bilan = bilan
        self.netID = netID

    def __str__(self):
        return f"id = {self.netID}, bilan = {self.bilan}"

    def toJSON(self):
        return json.dumps({
            "bilan": self.bilan,
            "netID": self.netID
        })


class Message:
    def __init__(self, contenu, emetteur, destinataire):
        self.contenu = contenu
        self.couleur = 0
        self.type = ""
        self.emetteur = emetteur
        self.destinataire = destinataire
        self.horloge = []

    def setcouleur(self, couleur):
        self.couleur = couleur

    def toJSON(self):
        return json.dumps({
            "contenu": self.contenu,
            "couleur": self.couleur,
            "type": self.type,
            "emetteur": self.emetteur,
            "destinataire": self.destinataire,
            "horloge": self.horloge
        })

    def toPrepost(self):
        copieMessage = copy.deepcopy(self)
        copieMessage.type = "prepost"
        return copieMessage


class MessageEtat(Message):
    def __init__(self, etat, emetteur, destinataire):
        super().__init__(etat.toJSON(), emetteur, destinataire)
        self.type = "etat"


class Net:
    def __init__(self, netID):
        self.netID = netID
        self.couleur = 0  # 0 = Blanc, 1 = Rouge
        self.initiateurSave = False
        self.bilanMessage = 0
        self.etatGlobal = list()
        self.nbMessageAttendu = 0
        self.nbEtatAttendu = 0

    def initSauvegarde(self):
        print("Initialisation de la sauvegarde")
        self.couleur = 1
        self.initiateurSave = True
        self.etatGlobal.append(Etat(self.netID))
        self.nbEtatAttendu = NbSite - 1
        self.nbMessageAttendu = self.bilanMessage

    def envoiMessageDeBase(self, message):
        print("Envoi message provenant de base")
        message.setcouleur(self.couleur)
        self.bilanMessage += 1
        # TODO, faire l'envoi de message dans la fonction

    def envoiMessageExterieur(self, message):
        print(f"envoie message : {message} depuis {self.netID}")
        # TODO, faire envoie à l'extérieur

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
            if m.couleur == 1 and self.couleur == 0:
                self.couleur = 1
                self.etatGlobal.append(Etat(self.bilanMessage, self.netID))
                self.envoiMessageExterieur(MessageEtat(Etat(self.netID, self.bilanMessage), self.netID, "UNK"))
            if m.couleur == 0 and self.couleur == 1:
                print("Passage au Prepost")
                self.envoiMessageExterieur(m.toPrepost())


if __name__ == '__main__':
    app1 = Net(1)
    app2 = Net(2)
    app3 = Net(3)

    etat1 = Etat(1, 0)

    m1 = Message("coucou", 2, 1)
    m2 = MessageEtat(etat1, 1, 2)

    app1.initSauvegarde()
    app1.receptionMessageExterieur(m1)
