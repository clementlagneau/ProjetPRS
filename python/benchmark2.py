from multiprocessing import Process,Pipe
import subprocess
import os
import time

def f(k):
    b = str(k)
    os.system("python3 server_client1_param.py 1234 "+b)

def g(a):
    b = str(a)
    subprocess.call(["/bin/bash","-c","(time ./client1 134.214.202.236 1234 out.txt 0) 2> log_"+b+".txt"])

def temps(path):
    with open(path,'r') as file:
        res = file.readlines()[1].split('\t')[1].split('m')
        sec = int(res[0]) * 60 + float(res[1].replace('s\n','').replace(',','.'))
    return(sec)

if __name__ == '__main__':
    for k in range(1,100,1):
        print("k vaut",k)
        p = Process(target=f, args=(k,))
        h = Process(target=g, args=(k,))
        p.start()
        time.sleep(1)
        h.start()
        p.join()
        h.join()

    with open('res.txt', 'w') as file:
        file.writelines("k" + ";" + "temps")
    for k in range(1,100,1):
        t = temps("log_"+str(k)+".txt")
        with open('res.txt','a') as file:
            file.writelines(k+";"+str(t))
