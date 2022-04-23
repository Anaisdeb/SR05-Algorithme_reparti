class VectClock:
    def __init__(self, i, N, tab):
        self.i = int(i)
        self.N = int(N)
        self.tab = tab

    def incr(self, otherClock):
        self.tab[self.i] += 1
        for j in range(self.N):
            self.tab[j] = max(int(self.tab[j]), int(otherClock.tab[j]))

    def __str__(self):
        strTab = "#".join(map(str, self.tab))
        return f"{self.i}#{self.N}#{strTab}"

    @classmethod
    def from_string(cls, s):
        content = s.split("#")
        return VectClock(content[0], content[1], content[2:])

class Etat:
    def __init__(self, netID, N, bilan=0):
        self.bilan = int(bilan)
        self.netID = int(netID)
        self.N = int(N)
        tab=[0 for x in range(self.N)]
        self.vectClock = VectClock(netID, N, tab)

    def __str__(self):
        return f"{self.netID}°{self.N}°{self.bilan}°{self.vectClock}"

    @classmethod
    def from_string(cls, s):
        contenu = s.split("°")
        etat = Etat(contenu[0], contenu[1], contenu[2])
        etat.vectClock = VectClock.from_string(contenu[3])
        return etat