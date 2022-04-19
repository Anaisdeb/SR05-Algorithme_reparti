from utils import eprint
from message import Message

'''
    parameter :  queue --> Queue where you put message sent on stdin
    
    Function that receive message on stdin, and put it in queue in order to be handled
    by BAS
'''


def send_message(queue):
    try:
        while True:
            message = Message.from_text(input())
            queue.put(message)
    except EOFError:
        eprint("stdin reached EOF, exiting")
        exit()


'''
    parameter :  
        receipt_queue --> Queue where are received messages
        queue --> Queue where you put message received by other machines

    Function that receive message from other machines, and put it in queue in order to be handled
    by BAS
'''


def receive_message(queue, receipt_queue):
    try:
        while True:
            # TODO : Est-ce que l'on considère que l'on va recevoir les messages dans une queue ?
            message = Message.from_text(receipt_queue.get())
            queue.put(message)
    except EOFError:
        eprint("stdout reached EOF, exiting")
        exit()
