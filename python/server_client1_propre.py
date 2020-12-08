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

def main():
    """
    Fonction principale du programme
    :return:
    """

    """
    ------------------------
    Debut du programme - Initialisation
    ------------------------
    """
    # Verifications des inputs
    if len(sys.argv) == 2 and 1000 <= int(sys.argv[1]) <= 9999 :
      port = int(sys.argv[1])
    else :
      print("Utilisation : /server Nport")
      return(-1)

    #Definitions des variables globales
    timeout = 0.03
    rtt = 0.02
    taille_fenetre_init = 40
    aug_taille_fenetre = 10
    taille_fenetre = taille_fenetre_init
    dernier_ack = 0
    nombre_client = 3000
    SIZE_BUFFER = 1024 #Taille du buffer
    rtt_moy = 0.005
    coeff_rtt = 1/taille_fenetre

    # Variables de metriques de performances
    retransmission = 0
    ack_ignore_debug = 0
    ack_ignore = 0
    fenetre_continue = 0
    ack_seules = 0

    # Creation des sockets
    sock_init = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('0.0.0.0', port)
    sock_init.bind(server_address)

    """
    ------------------------
    Debut de la connection
    ------------------------
    """

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

    #DEBUG
    temps_debut= time.time()

    """
    --------------------
    Envoie du fichier - 
    --------------------
    """

    def sendkton(k,n):
        #print("Send slice " + str(k) + "to" + str(n))
        for j in range(k, n + 1):
            sock_data.sendto((bytes(str(j).zfill(6), 'utf-8')) + file_cut[j - 1], address_client)
            time_file_cut[j] = time.time()
            #print("Send slice " + str(j) + " of total " + str(tot_seq))
        return(n)

    #On recupere le fichier
    try:
        data, address_client = sock_data.recvfrom(SIZE_BUFFER)
        print("Client wants file: " + data.decode())
        size = os.path.getsize(data.decode()[:-1])
        tot_seq = size // SIZE_BUFFER + 1
        print("Number of seq : ",tot_seq)
    except:
        print("We can't open the file, check out if the file is here")
        return(-1)

    #On decoupe le fichier
    with open(data.decode()[:-1], "rb") as file:
        # On calcul le nombre de sequences necessaires
        file_cut = []
        time_file_cut = [None for x in range(tot_seq + 1)]  # On initialise le tableau qui va stocker les temps d'envoi pour calculer le RTT
        for k in range(tot_seq):
            file_cut.append(copy.deepcopy((file.read(SIZE_BUFFER))))
        print("len file_cut", len(file_cut)) #DEBUG

    #Variables de gestion
    last_ack = False #Gestion du while
    change = False #Gestion dynamic window
    debut = True #Gestion retransmission
    while (not last_ack):
        sock_data.settimeout(coeff_rtt*rtt_moy)
        try:
            if dernier_ack == tot_seq:
                last_ack = True
                break
            elif debut:
                debut = False
                ack_ignore = 0
                fenetre_haut = min(dernier_ack+1+taille_fenetre, tot_seq)
                dernier_envoyer = sendkton(dernier_ack+1,fenetre_haut)
            elif change:
                change = False
                ack_ignore = 0
                fenetre_haut = min(dernier_ack+1+taille_fenetre,tot_seq)
                dernier_envoyer = sendkton(dernier_envoyer,fenetre_haut)
                taille_fenetre = min(taille_fenetre+aug_taille_fenetre,100)
            #print("Wait ACK")
            data, address_client = sock_data.recvfrom(SIZE_BUFFER)
            if data.decode()[:3] == "ACK":
                #print("Received " + data.decode())
                recu = int(data.decode()[3:9])
                rtt = time.time() - time_file_cut[recu]
                rtt_moy = (rtt_moy + rtt)/2
                #print("RTT : " + str(rtt),"Moy RTT",rtt_moy) # DEBUG
                if dernier_ack < recu :
                    #print("ACK > last one") #DEBUG
                    change = True
                    delta = min(recu - dernier_ack, taille_fenetre)
                    dernier_ack = recu
                    fenetre_continue += 1
                    """ 
                elif ack_ignore > 20 :
                    ack_ignore = 0
                    ack_ignore_debug += 1
                    #sendkton(recu+1,recu+1) #On met pas a jour dernier c'est normal
                    time.sleep(0.0002)
                    ack_seules += 1
                else:
                    #print("drop")
                    ack_ignore += 1
                    ack_ignore_debug += 1"""
            else: #DEBUG
                print("WTF BRO") #DEBUG
        except socket.error:
            debut = True
            #print("Retransmit")
            retransmission += 1
            taille_fenetre = taille_fenetre_init

    print("Send FIN")
    time.sleep(0.05) #
    sock_data.sendto("FIN".encode(), address_client)
    #DEBUG
    temps = time.time()-temps_debut
    print("Debit :",size,temps,size/temps)
    print("Retransmisions ",retransmission," | ACK_Ignores ", ack_ignore_debug, " | Fenetre continue ", fenetre_continue," | ACK seules ", ack_seules)
    print("File send")

if __name__ == '__main__':
    main()
