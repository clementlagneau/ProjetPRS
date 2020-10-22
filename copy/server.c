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
// On récupère le port d'écoute t'sais
  if(argc < 2){
    printf("Utilisez la syntaxe ./server PORT\n");
    return(EXIT_FAILURE);
  }

  struct sockaddr_in adresse;
  int port = atoi(argv[1]);
  int valid = 1; 
  char msg[RCVSIZE];
  //char blanmsg[RCVSIZE];

  //On crée la socket
  int server_desc = socket(AF_INET, SOCK_DGRAM , 0);

  //Au cas où
  if (server_desc < 0) { 
    perror("cannot create socket\n");
    return -1;
  }

  setsockopt(server_desc, SOL_SOCKET, SO_REUSEADDR, &valid, sizeof(int));
  adresse.sin_family= AF_INET;
  adresse.sin_port= htons(port);
  adresse.sin_addr.s_addr=htonl(INADDR_ANY);

  //On fait correspondre
  if(bind(server_desc, (struct sockaddr*)&adresse, sizeof(adresse)) < 0){
    perror("UDP bind failed \n");
    exit(EXIT_FAILURE);
  } 

  fd_set sock_set;
  FD_ZERO(&sock_set);
  
  int cont= 1;
  int not_initialized = 1;
  while (cont) {
    FD_SET(server_desc, &sock_set);
    printf("On ecoute ici\n");
    select(server_desc + 1, &sock_set, NULL, NULL, NULL);

    if(FD_ISSET(server_desc, &sock_set)){
      printf("Receive UDP\n" );
      int temp = sizeof(adresse);
      if(not_initialized) {
        printf("Wait for SYN\n");
        int n = recvfrom(server_desc, msg, RCVSIZE, 0, (struct sockaddr *) &adresse, (socklen_t *) &temp);
        if(n < 0){
          perror("recvfrom failed \n");
          exit(EXIT_FAILURE);
        }
        printf("Message 1 %s",msg);
        if(strncmp(msg,"SYN", 3) == 0){
          printf("SYN RECEIVED\n");
          strcpy(msg,"SYN-ACK");
          if (sendto(server_desc, msg, strlen(msg) , 0 , (struct sockaddr *) &adresse, sizeof(adresse)) < 0){
            perror("sendto");
            exit(EXIT_FAILURE);
          }
          printf("SYN-ACK sent");
          printf("Wait for ACK\n");
          n = recvfrom(server_desc, msg, RCVSIZE, 0, (struct sockaddr *) &adresse, (socklen_t *) &temp);
          if(n < 0){
            perror("recvfrom failed \n");
            exit(EXIT_FAILURE);
          }
          if(strncmp(msg,"ACK", 3) == 0){
          printf("ACK RECEIVED\n");
          }
        }
      }
      int n = recvfrom(server_desc, msg, RCVSIZE, 0, (struct sockaddr *) &adresse, (socklen_t *) &temp);
      if(n < 0){
        perror("recvfrom failed \n");
        exit(EXIT_FAILURE);
      }
      printf("Message 2 %s",msg);
      printf("Port : %hu, IP : %u\n",adresse.sin_port,adresse.sin_addr.s_addr);
      msg[n] = '\0';
      printf("DATA: %s\n", msg);
    }
  }
return 0;
}

