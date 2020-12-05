#!/usr/bin/env python3

import random
from multiprocessing import Process
from threading import Thread
import socket
import os
import time
import sys
import copy

def main():
    SIZE_BUFFER = 1024
    if len(sys.argv) == 3 and 1000 <= int(sys.argv[1]) <= 9999 :
      port = int(sys.argv[1])
      timeout = int(sys.argv[2])/10000
    else :
      print("Utilisation : /server Nport")
      return(-1)

    class Client(Thread):
        def __init__(self, port):
            Thread.__init__(self)
            self.port_data = port

        def run(self):
            print("We are in a new thread for a new client on port {}".format(port_data))
            sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            data_address = ('0.0.0.0', port_data)
            sock_data.bind(data_address)

            timeout = 0.002
            taille_fenetre = 20
            dernier_ack = 0

            # Variables de metriques de performances
            retransmission = 0
            ack_ignore_debug = 0
            ack_ignore = 0
            fenetre_continue = 0

            # Maintenant on fait le reste :
            data, address_client = sock_data.recvfrom(SIZE_BUFFER)
            print("Client wants file: " + data.decode())
            tot_seq = os.path.getsize(data.decode()[:-1]) // SIZE_BUFFER + 1
            print("Number of seq : ", tot_seq)
            with open(data.decode()[:-1], "rb") as file:
                # On calcul le nombre de sequences necessaires
                file_cut = []
                for k in range(tot_seq):
                    file_cut.append(copy.deepcopy((file.read(SIZE_BUFFER))))
                # On envoie le fichier petit a petit
                print("len file_cut", len(file_cut))
                # Il faut qu'on fasse les fenetres ici
                last_ack = False
                change = False
                debut = True
                while (not last_ack):
                    sock_data.settimeout(timeout)
                    try:
                        if dernier_ack == tot_seq:
                            # On a recu le dernier ACK
                            last_ack = True
                            break
                        if debut:
                            # Cas ou on revoie tout
                            ack_ignore = 0
                            debut = False
                            fenetre_haut = min(dernier_ack + 1 + taille_fenetre, tot_seq)
                            print("Send full slice " + str(dernier_ack + 1) + "to" + str(fenetre_haut))
                            for k in range(dernier_ack + 1, fenetre_haut + 1):
                                sock_data.sendto((bytes(str(k).zfill(6), 'utf-8')) + file_cut[k - 1], address_client)
                                print("Send slice " + str(k) + " of total " + str(tot_seq) + " of ",
                                      len(file_cut[k - 1]), " bits")
                        if change:
                            # Cas fenetre glissante
                            fenetre_haut = min(dernier_ack + 1 + taille_fenetre, tot_seq)
                            print("Send little slice " + str(dernier_ack + 1 + taille_fenetre - delta) + "to" + str(
                                fenetre_haut))
                            for k in range(dernier_ack + 1 + taille_fenetre - delta, fenetre_haut + 1):
                                sock_data.sendto((bytes(str(k).zfill(6), 'utf-8')) + file_cut[k - 1], address_client)
                                print("Send slice " + str(k) + " of total " + str(tot_seq) + " of ",
                                      len(file_cut[k - 1]), " bits")
                        print("Wait ACK")
                        data, address_client = sock_data.recvfrom(SIZE_BUFFER)
                        if data.decode()[:3] == "ACK":
                            print("Received " + data.decode())
                            recu = int(data.decode()[3:9])
                            if dernier_ack < recu:
                                # timeout = 0.9999 * timeout + 0.0005
                                # taille_fenetre = max(2 * taille_fenetre + 5 , 300)
                                print("ACK > last one")
                                change = True
                                delta = min(recu - dernier_ack, taille_fenetre)
                                dernier_ack = recu
                                fenetre_continue += 1
                            else:
                                if ack_ignore > 2:
                                    change = True
                                    print("Retransmit all")
                                    ack_ignore = 0
                                else:
                                    change = False
                                    ack_ignore += 1
                                ack_ignore_debug += 1
                    except socket.error:
                        timeout = 0.008
                        taille_fenetre = 30
                        debut = True
                        change = False
                        print("Retransmit")
                        retransmission += 1
            print("Send FIN")
            time.sleep(0.005)
            sock_data.sendto("FIN".encode(), address_client)
            # DEBUG
            print("Retransmisions ", retransmission, " | ACK_Ignores ", ack_ignore_debug, " | Fenetre continue ",
                  fenetre_continue)
            print("File send")

    timeout = 0.00001

    # Creation des sockets
    sock_init = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('0.0.0.0', port)
    sock_init.bind(server_address)

    while True:
        # Handshake of client and server
        handshake_success = False
        while not handshake_success:
            print("Wait SYN")
            data, address_client = sock_init.recvfrom(SIZE_BUFFER)
            print(data.decode())
            if data.decode()[:3] == "SYN":
                print("SYN received")

                #Il faut partir sur un nouveau process ICI
                port_data = random.randint(1000, 9999)
                c = Client(port_data)
                c.start()
                time.sleep(0.001)
                sock_init.sendto(("SYN-ACK" + str(port_data)).encode(), address_client)
                print("SYN received, just sent SYN-ACK"+str(port_data))
                data, address_client = sock_init.recvfrom(SIZE_BUFFER)
                if data.decode()[:3] == "ACK":
                    print("Received ACK")
                    handshake_success = True
        print("We are connected")




if __name__ == '__main__':
    main()
