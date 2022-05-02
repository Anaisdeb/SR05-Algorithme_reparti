import tkinter
from tkinter import messagebox
from messages import EditMessage
from utils import BasState

''' Class
    Bas : Class which represents base application
    
    attribute : 
        - net : instance of Net linked to base application,
        - state : content of Text zone in the base application,
        - root : contains tkinter instance,
        - requestSnapshotButton : instance of "Request a snapshot" button,
        - printTextWidget : instance of text content of application,
        - commandFrame / commandText : instance of Text Entry Frame and Entry for commands,
        - commandButton : instance for "Modifier" button
'''


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
        self.requestSnapshotButton = tkinter.Button(self.root, command=self.snapshot, text="Request a snapshot",
                                                    foreground="red")
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

    '''
        send(self, msg) --> send command to Bas (used by Net class in Net.sendToBas()) : 
                                - if command == "CsOk" :  edit from this instance of Bas
                                - else : edit from another instance of Bas
    '''

    def send(self, msg):
        if msg == "CsOk":
            self.doAction()
        else:
            try:
                command = Command.parse(msg)
                self.edit(command)
            except:
                self.net.logger("This is not a command")

    '''
        action(self) --> method linked to "Modifier" button,
                            ask for critical section, 
                            get command in Text entry,
                            disable button until the end of critical section
    '''

    def action(self):
        self.net.basCsRequest()
        self.state.isRequestingCs = True
        self.state.command = self.commandEntry.get()
        self.commandButton['state'] = 'disabled'
        self.commandEntry['state'] = 'disabled'

    '''
        doAction(self) --> parse command in command entry, modify text content and spread it to other Bas instance
    '''

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

    '''
        edit(self, command) --> execute command passed in parameter and write into text content, then disable it
    '''

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

    '''
        snapshot(self) --> Init a snapshot in net instance,
    '''

    def snapshot(self):
        self.net.initSnapshot()

    '''
        run(self) --> run Tkinter with this instance of Bas
    '''
    def run(self):
        self.root.mainloop()


''' Class
    Command : class which represents a command to enter in CommandEntry
    
    attribute : 
        - lineNumber : line of text content concerned by the command
        - action : action to realize on this line,
        - text : text to put if action is replcaing or inserting
        
    method : 
        - __str__(self) --> "lineNumber;action;text"
        - parse(cls, s) --> read a string and convert it into a command (static method) 
'''


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
