all : client server

client.o : client.c
	gcc -Wall -o client.o -c client.c

client : client.o
	gcc -Wall -o client client.o

server.o : server.c
	gcc -Wall -o server.o -c server.c

server : server.o
	gcc -Wall -o server server.o