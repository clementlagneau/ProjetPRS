#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define RCVSIZE 1024

int main (int argc, char *argv[]) {
  // Verification de la commande d execution
  if(argc < 2){
    printf("Utilisez la syntaxe ./server PORT\n");
    return(EXIT_FAILURE);
  }

  // Craft de notre adresse
  struct sockaddr_in adresse;
  int port = atoi(argv[1]);
  int valid = 1; 
  char msg[RCVSIZE];
  char head[11];

  // On crée la socket
  int server_desc = socket(AF_INET, SOCK_DGRAM , 0);
  // Verification de la creation de socket
  if (server_desc < 0) { 
    perror("cannot create socket\n");
    return(EXIT_FAILURE);
  }

  // Le RE USE c'est pour l'OS au cas ou
  setsockopt(server_desc, SOL_SOCKET, SO_REUSEADDR, &valid, sizeof(int));
  adresse.sin_family= AF_INET;
  adresse.sin_port= htons(port);
  adresse.sin_addr.s_addr=htonl(INADDR_ANY);

  //On fait correspondre la socket et le fichier
  if(bind(server_desc, (struct sockaddr*)&adresse, sizeof(adresse)) < 0){
    perror("UDP bind failed \n");
    exit(EXIT_FAILURE);
  } 
  
  int cont= 1;
  while (cont) {
    // On ecoute
    printf("On ecoute ici\n");
    printf("Wait for SYN\n");
    int temp = sizeof(adresse);
    int n = recvfrom(server_desc, msg, RCVSIZE, 0, (struct sockaddr *) &adresse, (socklen_t *) &temp);
    if(n < 0){
      perror("recvfrom failed \n");
      exit(EXIT_FAILURE);
    }
    printf("Message 1 %s \n",msg);
    if(strncmp(msg,"SYN", 3) == 0){
      printf("SYN RECEIVED\n");
      //Creation de la socket de donnee
      struct sockaddr_in adresse_donnee;
      int port_donnee = 3030;
      int valid=1;
      char msg_donnee[RCVSIZE];
      int server_desc_donnee = socket(AF_INET, SOCK_DGRAM , 0);
      //Au cas où
      if (server_desc < 0) { 
        perror("cannot create socket\n");
        return EXIT_FAILURE;
      }
      //Pour l OS au cas ou
      setsockopt(server_desc_donnee, SOL_SOCKET, SO_REUSEADDR, &valid, sizeof(int));
      adresse_donnee.sin_family= AF_INET;
      adresse_donnee.sin_port= htons(port_donnee);
      adresse_donnee.sin_addr.s_addr=htonl(INADDR_ANY);
      //On fait correspondre
      if(bind(server_desc_donnee, (struct sockaddr*)&adresse_donnee, sizeof(adresse_donnee)) < 0){
        perror("UDP bind failed \n");
        exit(EXIT_FAILURE);
      }
      strcpy(head,"SYN-ACK");
      char port_str[4];
      sprintf(port_str,"%d\n",port_donnee);
      strcat(head,port_str);
      printf("Head : %s \n",head);
//      strcpy(msg,"SYN-ACK_3030");
      if (sendto(server_desc, head, strlen(head) , 0 , (struct sockaddr *) &adresse, sizeof(adresse)) < 0){
        perror("sendto");
        exit(EXIT_FAILURE);
      }
      printf("SYN-ACK sent\n");
      printf("Wait for ACK\n");
      n = recvfrom(server_desc, msg, RCVSIZE, 0, (struct sockaddr *) &adresse, (socklen_t *) &temp);
      if(n < 0){
        perror("recvfrom failed \n");
        exit(EXIT_FAILURE);
      }
      if(strncmp(msg,"ACK", 3) == 0){
        printf("ACK RECEIVED\n");
      }
      while(cont){
        printf("On ecoute %u : %hu \n",ntohl(adresse_donnee.sin_addr.s_addr),ntohs(adresse_donnee.sin_port));
        int n = recvfrom(server_desc_donnee, msg_donnee, RCVSIZE, 0, (struct sockaddr *) &adresse, (socklen_t *) &temp);
        if(n < 0){
          perror("recvfrom failed \n");
          exit(EXIT_FAILURE);
        }
        printf("Message data %s \n",msg_donnee);
        printf("From %s : %hu \n",inet_ntoa(adresse.sin_addr),ntohs(adresse.sin_port));
        msg_donnee[n] = '\0';
        printf("Message : %s\n", msg_donnee);
      }
    }
  }
return 0;
}

