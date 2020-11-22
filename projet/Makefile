all : server

server.o : server.c
	gcc -Wall -o server.o -c server.c

server : server.o
	gcc -Wall -o server server.o

clean :
	rm *.o server