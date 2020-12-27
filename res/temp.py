def temps(path):
    with open(path,'r') as file:
        res = file.readlines()[1].split('\t')[1].split('m')
        sec = int(res[0]) * 60 + float(res[1].replace('s\n','').replace(',','.'))
    return(sec)

with open('res.txt', 'w') as file:
    file.writelines("k" + ";" + "j" + ";" + "temps")
for k in range(1,100,1):
    for j in range(1,100,1):
        try:
            t = temps("log_"+str(k)+"_"+str(j)+".txt")
            with open('res.txt', 'a') as file:
                file.write(str(k) + ";" + str(j) + ";" + str(t) + "\n")
        except Exception as inst:
            print(inst)
