import tkinter
from tkinter import messagebox
from messages import EditMessage
from utils import BasState

class Bas:
    def __init__(self, net):
        self.net = net
        self.state = BasState("""Bonjour
Ceci est un exemple de fichier texte à modifier

Utilisez l'entrée de commande en dessous pour le modifier :
    - 3;s;blabla
      Remplace la 3e ligne par blabla
    - 3;d;
      Supprime la 3e ligne
    - 3;a;blabla
      Ajoute la ligne blabla après la 3e ligne
    - 3;i;blabla
      Insère la ligne blabla avant la 3e ligne""")
        self.root = tkinter.Tk()
        self.requestSnapshotButton = tkinter.Button(self.root, command=self.snapshot, text="Request a snapshot", foreground="red")
        self.requestSnapshotButton.pack()
        self.printTextWidget = tkinter.Text(self.root)
        self.printTextWidget.insert("1.0", self.state.text)
        self.printTextWidget["state"] = "disabled"
        self.printTextWidget.pack()
        self.commandFrame = tkinter.Frame(self.root)
        self.commandFrame.pack()
        self.commandEntry = tkinter.Entry(self.commandFrame)
        self.commandEntry.pack()
        self.commandButton = tkinter.Button(self.commandFrame, command=self.action, text="Modifier")
        self.commandButton.pack()

    def send(self, msg):
        if msg == "CsOk":
            self.doAction()
        else:
            try:
                command = Command.parse(msg)
                self.edit(command)
            except:
                self.net.logger("This is not a command")

    def action(self):
        self.net.basCsRequest()
        self.state.isRequestingCs = True
        self.state.command = self.commandEntry.get()
        self.commandButton['state'] = 'disabled'
        self.commandEntry['state'] = 'disabled'

    def doAction(self):
        try:
            command = Command.parse(self.commandEntry.get())
            self.edit(command)
            self.net.sendMessageFromBas(EditMessage(self.net.netID, self.net.state.vectClock, self.commandEntry.get()))
        except:
            messagebox.showerror("Error", "Failed to apply command, please check command syntax")
        self.state.isRequestingCs = False
        self.commandButton['state'] = 'normal'
        self.commandEntry['state'] = 'normal'

    def edit(self, command):
        modified_text = self.state.text.split("\n")
        if command.action == "s":
            modified_text[command.lineNumber - 1] = command.text
        elif command.action == "a":
            modified_text.insert(command.lineNumber, command.text)
        elif command.action == "i":
            modified_text.insert(command.lineNumber - 1, command.text)
        else:
            del modified_text[command.lineNumber - 1]
        self.state.text = "\n".join(modified_text)
        self.printTextWidget["state"] = "normal"
        self.printTextWidget.delete("1.0", tkinter.END)
        self.printTextWidget.insert("1.0", self.state.text)
        self.printTextWidget["state"] = "disabled"

    def snapshot(self):
        self.net.initSnapshot()

    def run(self):
        self.root.mainloop()

class Command:
    def __init__(self, lineNumber, action, text):
        self.lineNumber = int(lineNumber)
        self.action = action
        self.text = text

    def __str__(self):
        return f"{self.lineNumber};{self.action};{self.text}"

    @classmethod
    def parse(cls, s):
        content = s.split(";")
        text = ";".join(content[2:])
        return Command(content[0], content[1], text)

if __name__ == "__main__":
    app = Bas()
    app.run()
