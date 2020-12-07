#!/usr/bin/env python3
"""
Projet PRS INSA 4TC2
Hugo Courte - Clement Lagneau
"""
import socket
import os
import time
import sys
import copy

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def main():
    """Fonction princiaple
    """
    SIZE_BUFFER = 1024 #Taille du buffer
    #Verification des parametres d entree
    if len(sys.argv) == 2 and 1000 <= int(sys.argv[1]) <= 9999 :
      port = int(sys.argv[1])
    else :
      print("Utilisation : /server Nport")
      return(-1)

    #Definitions des variables globales
    timeout = 0.03
    rtt = 0.002
    coeff_rtt = 1
    aug_taille_fenetre = 2
    taille_fenetre = 20
    dernier_ack = 0
    nombre_client = 3000

    # Creation des sockets
    sock_init = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('0.0.0.0', port)
    sock_init.bind(server_address)

    # Handshake of client and server
    handshake_success = False
    while not handshake_success:
        print("Wait SYN")
        data, address_client = sock_init.recvfrom(SIZE_BUFFER)
        print(data.decode())
        if data.decode()[:3] == "SYN":
            print("SYN received")

            # On cree la socket de donnee
            sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            port_data = nombre_client
            nombre_client = (nombre_client + 1)
            data_address = ('0.0.0.0', port_data)
            sock_data.bind(data_address)

            sock_init.sendto(("SYN-ACK" + str(port_data)).encode(), address_client)
            print("SYN received, just sent SYN-ACK"+str(port_data))
            data, address_client = sock_init.recvfrom(SIZE_BUFFER)
            if data.decode()[:3] == "ACK":
                print("Received ACK")
                handshake_success = True
    print("We are connected")


    # Variables de metriques de performances
    retransmission = 0
    ack_ignore_debug = 0
    ack_ignore = 0
    fenetre_continue = 0

    #Maintenant on fait le reste :
    data, address_client = sock_data.recvfrom(SIZE_BUFFER)
    print("Client wants file: " + data.decode())
    tot_seq = os.path.getsize(data.decode()[:-1]) // SIZE_BUFFER + 1
    print("Number of seq : ",tot_seq)
    with open(data.decode()[:-1],"rb") as file :
        #On calcul le nombre de sequences necessaires
        file_cut = []
        time_file_cut = [None for x in range (tot_seq+1)] #On initialise le tableau qui va stocker les temps d'envoi pour calculer le RTT
        for k in range(tot_seq):
            file_cut.append(copy.deepcopy((file.read(SIZE_BUFFER))))
        #On envoie le fichier petit a petit
        print("len file_cut",len(file_cut))
        #Il faut qu'on fasse les fenetres ici
        last_ack = False
        change = False
        debut = True
        while (not last_ack):
            sock_data.settimeout(min(coeff_rtt*rtt, timeout))
            try:
                if dernier_ack == tot_seq:
                    #On a recu le dernier ACK
                    last_ack = True
                    break
                if debut:
                    #Cas ou on revoie tout
                    ack_ignore = 0
                    debut = False
                    fenetre_haut = min(dernier_ack+1+taille_fenetre,tot_seq)
                    print("Send full slice "+str(dernier_ack+1)+"to"+str(fenetre_haut))
                    for k in range(dernier_ack+1,fenetre_haut+1):
                        sock_data.sendto((bytes(str(k).zfill(6),'utf-8'))+file_cut[k-1], address_client)
                        time_file_cut[k] = time.time() #On récupère le temps pour chaque segment qu'on envoie pour rtt
                        print("Send slice " + str(k) + " of total " + str(tot_seq) + " of ",
                              len(file_cut[k-1]), " bits")
                if change:
                    #Cas fenetre glissante
                    fenetre_haut = min(dernier_ack+1+taille_fenetre+1,tot_seq)
                    print("Send little slice "+str(dernier_ack+1+taille_fenetre-delta)+"to"+str(fenetre_haut))
                    for k in range(dernier_ack+1+taille_fenetre-delta,fenetre_haut+1):
                        sock_data.sendto((bytes(str(k).zfill(6),'utf-8'))+file_cut[k-1], address_client)
                        time_file_cut[k] = time.time() #On récupère le temps pour chaque segment qu'on envoie pour calcul rtt
                        print("Send slice " + str(k) + " of total " + str(tot_seq) + " of ",
                              len(file_cut[k-1]), " bits")
                print("Wait ACK")
                data, address_client = sock_data.recvfrom(SIZE_BUFFER)
                if data.decode()[:3] == "ACK":
                    print("Received "+data.decode())
                    recu = int(data.decode()[3:9])
                    rtt = time.time() - time_file_cut[recu] #On calcule rtt entre temps paquet validé et temps original
                    print("RTT : " + str(rtt))
                    if dernier_ack < recu:
                        #timeout = 0.9999 * timeout + 0.0005
                        #taille_fenetre = max(2 * taille_fenetre + 5 , 300)
                        print("ACK > last one")
                        change = True
                        delta = min(recu - dernier_ack,taille_fenetre)
                        dernier_ack = recu
                        fenetre_continue +=1
                        #timeout = 0.01
                        #taille_fenetre += aug_taille_fenetre
                    else:
                        if ack_ignore > 4:
                            #debut = True
                            time.sleep(0.001)
                            print("Retransmit all")
                            ack_ignore = 0
                            sock_data.sendto((bytes(str(dernier_ack+1).zfill(6), 'utf-8')) + file_cut[dernier_ack], address_client)
                        else:
                            change = False
                            ack_ignore +=1
                        ack_ignore_debug +=1
            except socket.error:
                timeout = 0.03
                taille_fenetre = 30
                debut = True
                change = False
                print("Retransmit")
                retransmission +=1
    print("Send FIN")
    time.sleep(0.005)
    sock_data.sendto("FIN".encode(), address_client)
    #DEBUG
    print("Retransmisions ",retransmission," | ACK_Ignores ", ack_ignore_debug, " | Fenetre continue ", fenetre_continue)
    print("File send")








if __name__ == '__main__':
    main()