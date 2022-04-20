#!/bin/python3 
import sys
import os
import fileinput
import time
import threading
import queue
import json
import argparse


otherAppID = sys.argv[1]
appID = sys.argv[2]

class Message:
	def __init__(self, who, what):
		self.who = who#A qui
		self.what = what#contenu
	def __str__(self):
		return json.dumps({
			"who": self.who,
			"what": self.what
		})

def MessageFromJson(s):
    d = json.loads(s)
    return Message(d["who"], d["what"])

def lecture(q):
	for line in sys.stdin:
		q.put(MessageFromJson(line))

def ecriture(q, l):#écrire message périodique sur stdout
	while(l.is_alive()):
		q.put(Message(otherAppID, "test"))
		time.sleep(2)

#arrivée d'un message => ajouter événement message en tête de file
#travail à faire => ajouter événement travail en tête de file
def centurion(q, l, e):
	while(not(q.empty()) or (l.is_alive() and e.is_alive())):
		#lire événement en tête de file /* lecture bloquante */
		message = q.get()
		if message.who == appID:
			print(message.what, file=sys.stderr, flush=True)
		else: 
			print(message, file=sys.stdout, flush=True)

if __name__ == "__main__":
	evts = queue.Queue(maxsize=0)
	l = threading.Thread(target=lecture, args=(evts,))
	e = threading.Thread(target=ecriture, args=(evts,l))
	c = threading.Thread(target=centurion, args=(evts,l,e))
	l.start()
	e.start()
	c.start()
	l.join()
	e.join()
	c.join()
