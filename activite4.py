import asyncio
import os
import signal
import sys
import time
from tkinter import *
from tkinter import ttk


stdinValueVar = "Aucune entrée"
stdoutValueVar = "Message standard \n"


async def connect_stdin():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return reader


async def child():
    global stdinValueVar
    reader = await connect_stdin()
    while True:
        res = await reader.read(100)
        stdinValueVar = res.decode("utf-8")
        os.kill(os.getppid(), signal.SIGSTOP)
        os.kill(os.getppid(), signal.SIGCONT)


def stdoutButtonCallback():
    global stdoutValueVar
    stdoutValueVar = stdoutEntry.get()


def Act4behavior():
    timer = time.time()
    pid = os.fork()
    if pid == 0:
        asyncio.run(child())
    else:
        while True:
            # sys.stdout.write("Message")
            stdinValue.set(stdinValueVar)
            if time.time() - timer > 5:
                sys.stdout.write(stdoutValueVar)
                timer = time.time()


if __name__ == '__main__':
    rootPage = Tk()
    mainFrame = ttk.Frame(rootPage, padding=0)
    mainFrame.grid()

    stdoutLabel = ttk.Label(mainFrame, text="Text à afficher sur stdout!")
    stdoutLabel.grid(column=0, row=0)
    stdoutEntry = ttk.Entry(mainFrame)
    stdoutEntry.grid(column=1, row=0)
    stdoutButton = ttk.Button(mainFrame, text="Valider les changements", command=stdoutButtonCallback)
    stdoutButton.grid(column=2, row=0)

    stdinLabel = ttk.Label(mainFrame, text="Text affiché dans stdin")
    stdinLabel.grid(column=0, row=1)
    stdinValue = StringVar()
    stdinValue.set(stdinValueVar)
    stdinValueLabel = ttk.Label(mainFrame, textvariable=stdinValue)
    stdinValueLabel.grid(column=1, row=1)

    rootPage.mainloop()
