from multiprocessing import Process,Pipe
import subprocess
import os
import time

def f(n):
    subprocess.call(['/bin/bash', '-c',"python3 server_test.py 1234"])

def g(n):
    n.send(subprocess.check_call(['/bin/bash', '-c',"time ./client1 134.214.202.236 1234 chat.jpg | grep real >> res.txt "]))
    n.close()

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=f, args=("",))
    h = Process(target=g, args=(child_conn,))
    p.start()
    time.sleep(1)
    h.start()
    p.join()
    h.join()
    print("Fin", parent_conn.recv())
