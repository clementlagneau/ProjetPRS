from multiprocessing import Process,Pipe
import subprocess
import os
import time

def f(k):
    os.system("python3 server_test.py 1234")

def g(k):
    subprocess.call(["/bin/bash","-c","(time ./client1 134.214.202.236 1234 test.txt "+str(k)+" >> log_"+str(k)+".txt 2>&1"])

if __name__ == '__main__':
    for k in range(5,1000,5):
        p = Process(target=f, args=("k",))
        h = Process(target=g, args=("k",))
        p.start()
        time.sleep(1)
        h.start()
        p.join()
        h.join()
