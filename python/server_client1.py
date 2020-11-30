#
#!/usr/bin/env python3
import socket
import os
import time
import sys
import copy

def main():
    SIZE_BUFFER = 1024
    if len(sys.argv) == 2 and 1000 <= int(sys.argv[1]) <= 9999 :
      port = int(sys.argv[1])
    else :
      print("Utilisation : /server Nport")
      return(-1)

    timeout = 0.001
    taille_fenetre = 20
    dernier_ack = 0

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
            port_data = 3030
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
    #Maintenant on fait le reste :
    while True:
        data, address_client = sock_data.recvfrom(SIZE_BUFFER)
        print("Client wants file: " + data.decode())
        tot_seq = os.path.getsize(data.decode()[:-1]) // SIZE_BUFFER + 1
        print("Number of seq : ",tot_seq)
        with open(data.decode()[:-1],"rb") as file : #On vire le \o de la fin t sais
            #On calcul le nombre de sequences necessaires
            file_cut = []
            for k in range(tot_seq):
                file_cut.append(copy.deepcopy((file.read(SIZE_BUFFER))))
            #On envoie le fichier petit a petit
            print("len file_cut",len(file_cut))
            #Il faut qu'on fasse les fenetres ici
            last_ack = False
            while (not last_ack):
                sock_data.settimeout(timeout)
                try:
                    if dernier_ack == tot_seq:
                        last_ack = True
                        break
                    fenetre_haut = min(dernier_ack+1+taille_fenetre,tot_seq)
                    print("Send slice "+str(dernier_ack+1)+"to"+str(dernier_ack+1+taille_fenetre))
                    for k in range(dernier_ack+1,fenetre_haut+1):
                        sock_data.sendto((bytes(str(k).zfill(6),'utf-8'))+file_cut[k-1], address_client)
                        print("Send slice " + str(k) + " of total " + str(tot_seq) + " of ",
                              len(file_cut[k-1]), " bits")
                    print("Wait ACK")
                    data, address_client = sock_data.recvfrom(SIZE_BUFFER)
                    if data.decode()[:3] == "ACK":
                        print("Received "+data.decode())
                        dernier_ack = int(data.decode()[3:9])
                except socket.error:
                    print("Retransmit")
            sock_data.sendto("FIN".encode(), address_client)
            break
    #DEBUG
    print("File send")








if __name__ == '__main__':
    main()