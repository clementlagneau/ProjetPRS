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
  
  //Craft de notre adresse
  struct sockaddr_in adresse;
  int port = atoi(argv[1]);
  int valid = 1; 
  char msg[RCVSIZE];
  FILE *file;

  //On crée la socket
  int server_desc = socket(AF_INET, SOCK_DGRAM , 0);

  //Au cas où
  if (server_desc < 0) { 
    perror("cannot create socket\n");
    return(EXIT_FAILURE);
  }

  //Le RE USE au cas ou pour l OS
  setsockopt(server_desc, SOL_SOCKET, SO_REUSEADDR, &valid, sizeof(int));
  adresse.sin_family= AF_INET;
  adresse.sin_port= htons(port);
  adresse.sin_addr.s_addr=htonl(INADDR_ANY);

  //On fait correspondre
  if(bind(server_desc, (struct sockaddr*)&adresse, sizeof(adresse)) < 0){
    perror("UDP bind failed \n");
    exit(EXIT_FAILURE);
  } 

  
  int cont= 1;
  int not_initialized = 1;
  while (cont) {
  printf("On ecoute ici\n");
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
        not_initialized=0;
        }
      }
    }
    int n = recvfrom(server_desc, (char *)msg, RCVSIZE,MSG_WAITALL, ( struct sockaddr *) &adresse, &temp); 
    if(n < 0){
      perror("recvfrom failed \n");
      exit(EXIT_FAILURE);
    }
    // ON EST CONNECTE
    msg[n] = '\0';
    file = NULL;
    if((file=fopen(msg,"r")) == NULL){
      printf("Not able to open file\n");
      exit(EXIT_FAILURE);
    }
    size_t pos = ftell(file);    // Current position
    fseek(file, 0, SEEK_END);    // Go to end
    size_t length = ftell(file); // read the position which is the size
    fseek(file, pos, SEEK_SET);
    char lecture_buffer[length]; // Attention a la taille du fichier
    
    if((fread(lecture_buffer,sizeof(char),length,file))!=length){
        printf("Not able to read file..\n");
    }
    fclose(file);

    printf("File has a size of %d bytes\n",length);

    int segment_number;
      int rest = length % (RCVSIZE-6);
      if((length % (RCVSIZE-6)) != 0){
          segment_number = (length/(RCVSIZE-6))+1;
      } 
      else {
          segment_number = length/(RCVSIZE-6);
      }        
      
    printf("The file sent will be in %d segments\n",segment_number);

    int ack = 0;
    char num_seq_tot[7];
    char num_seq_s[7];
    int last_segment = 0;
    int numbytes;

    for(int num_seq=0;num_seq < segment_number;num_seq++){ //Grosse boucle d'envoi
        printf("DEBUT FOR : num seq = %d, seq_num = %d",num_seq, segment_number);
        if(num_seq == segment_number-1){
            last_segment = 1;
            printf("attention last segment\n");
        }
        printf("Sequence number %d\n",num_seq);
        memcpy(msg+6, lecture_buffer+((RCVSIZE-6)*num_seq), RCVSIZE-6);
        strcpy(num_seq_tot, "000000");
        
        snprintf((char *) num_seq_s, 10, "%d", num_seq); //ACK_XXXXXX
        for(int i = strlen(num_seq_s);i>=0;i--){
            num_seq_tot[strlen(num_seq_tot)-i]=num_seq_s[strlen(num_seq_s)-i];
        }
        memcpy(msg,num_seq_tot, 6);
        ack = 0;
        while(ack == 0){
          printf("On rentre dans le while");
            if(last_segment == 1){
                numbytes = rest;
            }
            else {
                numbytes = RCVSIZE;
            }
            printf("ok copy\n");
            sendto(server_desc,(const char*)msg, numbytes ,MSG_CONFIRM, (const struct sockaddr *) &adresse,temp);
            //printf("MSG : %s", msg);
            n = recvfrom(server_desc, (char *)msg, RCVSIZE,MSG_WAITALL, (struct sockaddr *) &adresse,&temp); 
            if(n < 0){
              perror("recvfrom failed \n");
              exit(EXIT_FAILURE);
            }
            msg[n] = '\0';
            
            char numack_s[7] = "";
            strncat(numack_s, strtok(msg,"ACK_"), 6);
            int numack = atoi(numack_s);
            //int numack = atoi(strtok(msg,"ACK_"));
            
            if( numack == num_seq){
                printf("String numack : %s\n",numack_s);
                printf("Nous avons recu %d",numack);
                ack = 1;
                printf("Acquitement de %d est reussi\n",num_seq);
            }
            else{
              printf("String numack : %s\n",numack_s);
              printf("Numack %d", numack);
              printf("Numseq %d", num_seq);
            }
          printf("On sort du while\n");
          }
      printf("On sort du for\n");
      }
  printf("bien sorti de la boucle\n");
  char message[RCVSIZE];
  strcpy(message,"END");
  sendto(server_desc, message, RCVSIZE, MSG_CONFIRM, (const struct sockaddr *) &adresse,temp);
  printf("Waiting for final ACK\n");
  n = recvfrom(server_desc, (char *)msg, RCVSIZE,MSG_WAITALL, (struct sockaddr *) &adresse,&temp); 
  msg[n] = '\0';
  printf("Final ack done.\n");
  }
return 0;
}


