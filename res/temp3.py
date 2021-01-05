max_1 = 1000
max_2 = 1000
max_3 = 1000

with open('res.txt','r') as file:
    for line in file.readlines():
        if float(t[2].replace("\n","")) < max_3:
            max_1 = float(t[0])
            max_2 = float(t[1])
            max_3 = float(t[2].replace("\n",""))

print(max_1,max_2,max_3)


