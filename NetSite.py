#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse


class Message:
    # Format d'un message
    def __init__(self, writer, reader, stamp, messageType):
        self.writer = writer
        self.reader = reader
        self.stamp = stamp
        self.type = messageType


class NetSite:
    def __init__(self, nameValue, neighborsValue):
        # Initialisation du nom du site
        self.name = nameValue
        # Initialisation de l'estampille du site
        self.stamp = 0
        # Initialisation des sites du réseau
        network = neighborsValue.split(",")
        network.append(self.name)
        print("\nListe des sites du réseau : ", network)

        # Initialisation de la table du site, de type dictionnaire
        # Avec clé = nom du site, valeur = tuple (type, date logique) du site
        # type ∈ {R, L, A} pour {Requête, Libération, Accusé}
        # date logique ∈ ℕ
        self.tab = {}
        for nomSite in network:
            self.tab[nomSite] = ('L', 0)
        print("\nTab du site : ", self.tab)

    def send(self, msg):
        # Envoie d'un message à un destinataire
        print("envoi d'un message de type,", msg.type, ", date logique : ", msg.stamp, ", du site ", msg.writer,
              "au site ", msg.reader)
        # TODO : gestion des communications

    def bas_sc_request(self):
        # NET reçoit une demande de section critique de l'application BAS
        self.stamp += 1
        msg = Message(self.name, 'ALL', self.stamp, 'R')
        self.tab[self.name] = ('R', self.stamp)
        self.send(msg)

    def bas_sc_release(self):
        # NET reçoit une fin de section critique de l'application BAS
        self.stamp += 1
        msg = Message(self.name, 'ALL', self.stamp, 'L')
        self.tab[self.name] = ('L', self.stamp)
        self.send(msg)

    def msg_request(self, msg):
        # NET reçoit un message de type requête d'une autre application
        writer_stamp = msg.stamp
        self.stamp = max(self.stamp, writer_stamp) + 1
        self.tab[msg.writer] = ('R', writer_stamp)
        # Envoie accusé au site demandeur
        msg = Message(self.name, msg.writer, self.stamp, 'A')
        self.send(msg)
        # Vérification de l'état d'une éventuelle demande du site
        self.status_check()

    def msg_release(self, msg):
        # NET reçoit un message de type libération d'une autre application
        writer_stamp = msg.stamp
        self.stamp = max(self.stamp, writer_stamp) + 1
        self.tab[msg.writer] = ('L', writer_stamp)
        # Vérification de l'état d'une éventuelle demande du site
        self.status_check()

    def msg_accused(self, msg):
        # NET reçoit un message de type accusé d'une autre application
        writer_stamp = msg.stamp
        self.stamp = max(self.stamp, writer_stamp) + 1
        # On n’écrase pas la date d’une requête par celle d’un accusé
        if self.tab[msg.writer][0] != 'R':
            self.tab[msg.writer] = ('A', writer_stamp)
        # Vérification de l'état d'une éventuelle demande du site
        self.status_check()

    def status_check(self):
        site_status = self.tab[self.name][0]
        # Si le site est en demande de section critique
        if site_status == 'R':
            # Le site dont la requête est la plus ancienne dans le réseau
            smallest_site_req = min(self.tab, key=lambda k: self.tab[k][1])
            # S'il est le site qui a la plus petite estampille
            if smallest_site_req == self.name:
                # Ce site peut entrer en section critique
                self.sc_entry()

    def sc_entry(self):
        # Le site entre en section critique
        print("Le site ", self.name, " entre en section critique")
        # TODO : NET envoie à BAS l'autorisation d'entrer
        # Le site libère la section critique
        self.bas_sc_release()


if __name__ == '__main__':
    # Parsing des arguments
    parser = argparse.ArgumentParser(description='site creation')
    parser.add_argument('-name', help='name of the site to create', required=True)
    parser.add_argument('-neighbors', help='name of the other sites in the same network (separated by a comma)',
                        required=True)
    args = parser.parse_args()
    name = args.name
    neighbors = args.neighbors

    # Lancement du contrôle du site
    site = NetSite(name, neighbors)
