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

  //Craft de l adresse
  char ip_server[15];
  struct sockaddr_in adresse;
  int port = atoi(argv[2]);
  strcpy(ip_server, argv[1]); 
  int valid = 1; 
  char msg[RCVSIZE];

  //Pour après
  int port_donnee = 0;

  //On crée la socket
  int server_desc = socket(AF_INET, SOCK_DGRAM , IPPROTO_UDP);

  // Au cas où
  if (server_desc < 0) { 
    perror("cannot create socket\n");
    return -1;
  }

  //Pour l OS
  setsockopt(server_desc, SOL_SOCKET, SO_REUSEADDR, &valid, sizeof(int));
  adresse.sin_family= AF_INET;
  adresse.sin_port= htons(port);
  inet_aton(ip_server,&adresse.sin_addr);

  //Envoie d un SYN
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
    //On recupere le nouveau port :
    char port_str[6];
    strcpy(port_str,strtok(msg,"SYN-ACK_"));
    printf("Nouveau port : %s", port_str);
    port_donnee = atoi(port_str);
//    printf("Nouveau port : %d", numport);
    strcpy(msg,"ACK");
    if (sendto(server_desc, msg, strlen(msg) , 0 , (struct sockaddr *) &adresse, sizeof(adresse)) < 0){
      perror("sendto");
      exit(EXIT_FAILURE);
    }
    printf("ACK sent \n");
  }
  else{
    printf("SYN-ACK FAILED\n");
    printf("%s",msg);
    return(EXIT_FAILURE);
  }

  int cont= 1;
  while (cont) {
    printf("Enter message : ");
		fgets(msg, RCVSIZE, stdin);
		//Envoie du message
    int server_desc_donnee = socket(AF_INET, SOCK_DGRAM , IPPROTO_UDP);
    if (server_desc_donnee < 0) { 
      perror("cannot create socket\n");
    return EXIT_FAILURE;
    }
    setsockopt(server_desc_donnee, SOL_SOCKET, SO_REUSEADDR, &valid, sizeof(int));
    struct sockaddr_in adresse_donnee;
    adresse_donnee.sin_family= AF_INET;
//    int port_donnee= 3030;
    adresse_donnee.sin_port= htons(port_donnee);  
    inet_aton(ip_server,&adresse_donnee.sin_addr);
		if (sendto(server_desc_donnee, msg, strlen(msg) , 0 , (struct sockaddr *) &adresse_donnee, sizeof(adresse_donnee)) < 0){
      perror("sendto");
      exit(EXIT_FAILURE);
    }
    printf("Msg envoyé à %s via %hu !\n",inet_ntoa(adresse_donnee.sin_addr),ntohs(adresse_donnee.sin_port));
    }
return(0);
}

