class VectClock:
    def __init__(self, i, N, tab):
        self.i = i
        self.N = N
        self.tab = tab

    def incr(self, otherClock):
        self.tab[self.i] += 1
        for j in range(self.N):
            self.tab[j] = max(self.tab[j], otherClock.tab[j])

    def __str__(self):
        strTab = "#".join(map(str, self.tab))
        return f"{self.i}#{self.N}#{strTab}"

    @classmethod
    def from_string(cls, s):
        content = s.split("#")
        return VectClock(content[0], content[1], content[2:])
