from multiprocessing import Process,Pipe
import subprocess
import os
import time

def f(n):
    os.system("python3 server_test.py 1234")

def g(n):
    subprocess.call(["/bin/bash","-c","(time ./client1 134.214.202.236 1234 test.txt) >> log.txt 2>&1"])

if __name__ == '__main__':
    p = Process(target=f, args=("",))
    h = Process(target=g, args=("",))
    p.start()
    time.sleep(1)
    h.start()
    p.join()
    h.join()
