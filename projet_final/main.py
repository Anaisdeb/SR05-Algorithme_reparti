from queue import Queue
from threading import Thread
from net import receive_message, send_message

q = Queue()
receipt_q = Queue()


if __name__ == "__main__":
    receive_thread = Thread(target=receive_message(q, receipt_q))
    send_thread = Thread(target=send_message(q))
