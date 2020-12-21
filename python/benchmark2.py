from multiprocessing import Process,Pipe
import subprocess
import os
import time

def f(temp):
    b = str(temp[0])
    c = str(temp[1])
    os.system("python3 server_client1_param.py 1234 "+b+" "+c)

def g(temp):
    b = str(temp[0])
    c = str(temp[1])
    subprocess.call(["/bin/bash","-c","(time ./client1 134.214.202.27 1234 out.txt 0) 2> log_"+b+"_"+c+".txt"])

def temps(path):
    with open(path,'r') as file:
        res = file.readlines()[1].split('\t')[1].split('m')
        sec = int(res[0]) * 60 + float(res[1].replace('s\n','').replace(',','.'))
    return(sec)

if __name__ == '__main__':
    for k in range(1,100,1):
        for l in range(1,100,1):
            print('avance 1')
            temp = (k,j)
            p = Process(target=f, args=(temp,)
            h = Process(target=g, args=(temp,)
            p.start()
            time.sleep(1)
            h.start()
            p.join()
            h.join()

    with open('res.txt', 'w') as file:
        file.writelines("k" + ";" + "temps")
    for k in range(1,100,1):
        for j in range(1,100,1):
            t = temps("log_"+str(k)+"_"+str(j)".txt")
            with open('res.txt','a') as file:
                file.write(str(k)+";"+str(j)+";"+str(t)+"\n")
