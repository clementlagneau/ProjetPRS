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
//On recupere le port et ip destination
  if(argc < 3){
    printf("Utilisez la syntaxe ./client IP PORT\n");
    return(EXIT_FAILURE);
  }

  char ip_server[15];
  struct sockaddr_in adresse;
  int port = atoi(argv[2]);
  strcpy(ip_server, argv[1]); 
  int valid = 1; 
  char msg[RCVSIZE];
  //char blanmsg[RCVSIZE];

  //On crée la socket
  int server_desc = socket(AF_INET, SOCK_DGRAM , IPPROTO_UDP);

  // Au cas où
  if (server_desc < 0) { 
    perror("cannot create socket\n");
    return -1;
  }

  setsockopt(server_desc, SOL_SOCKET, SO_REUSEADDR, &valid, sizeof(int));
  adresse.sin_family= AF_INET;
  adresse.sin_port= htons(port);
  inet_aton(ip_server,&adresse.sin_addr);
  strcpy(msg, "SYN\0"); 
  if (sendto(server_desc, msg, strlen(msg) , 0 , (struct sockaddr *) &adresse, sizeof(adresse)) < 0){
    perror("sendto");
    exit(EXIT_FAILURE);
    }
  printf("SYN sent\n");
  printf("Waiting for SYN-ACK\n");
  int temp = sizeof(adresse);
  int n = recvfrom(server_desc, msg, RCVSIZE, 0, (struct sockaddr *) &adresse, (socklen_t *) &temp);
  if(n < 0){
    perror("recvfrom failed \n");
    exit(EXIT_FAILURE);
  }
  if(strncmp(msg,"SYN-ACK", 7) == 0){
    printf("SYN-ACK RECEIVED\n");
    strcpy(msg,"ACK");
          if (sendto(server_desc, msg, strlen(msg) , 0 , (struct sockaddr *) &adresse, sizeof(adresse)) < 0){
            perror("sendto");
            exit(EXIT_FAILURE);
          }
          printf("ACK sent");
  }

  int cont= 1;
  while (cont) {
    printf("Enter message : ");
		fgets(msg, RCVSIZE, stdin);
		//Envoie du message
		if (sendto(server_desc, msg, strlen(msg) , 0 , (struct sockaddr *) &adresse, sizeof(adresse)) < 0){
            perror("sendto");
            exit(EXIT_FAILURE);
        }
    printf("Msg envoyé !\n");
    }
  return(0);
  }

