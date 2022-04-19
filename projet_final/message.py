from utils import eprint

'''
    Copier coller de la classe message du projet de Robin Bouvier, elle fait le café
'''
class Message:
    # Définit le format des messages : "{sender}~{dest}~{type}~{content}"
    def __init__(self, sender, dest, mtype, content):
        self.sender = sender
        self.dest = dest
        self.mtype = mtype
        self.content = content

    def __str__(self):
        return "{}~{}~{}~{}".format(self.sender, self.dest, self.mtype, self.content)

    @classmethod
    def from_text(cls, text):
        # Extrait le contenu des messages
        content = text.split('~')
        return Message(content[0], content[1], content[2], content[3])

    # pong : retour de la vague. Réponse de chaque site au ping
    def __init__(self, sender, dest, content):
        self.sender = sender
        self.dest = dest
        self.mtype = "message_received"
        self.content = content


if __name__ == "__main__":
    pass
