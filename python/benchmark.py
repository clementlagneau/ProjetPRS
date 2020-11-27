from multiprocessing import Process
from subprocess import call
import os
import time

def f(n):
    call(['/bin/bash', '-c',"python3 server_test.py 1234"])

def g(n):
    call(['/bin/bash', '-c',"time ./client1 134.214.202.220 1234 chat.jpg"])

if __name__ == '__main__':
    p = Process(target=f, args=("",))
    h = Process(target=g, args=("",))
    p.start()
    time.sleep(1)
    h.start()
    p.join()
    h.join()
