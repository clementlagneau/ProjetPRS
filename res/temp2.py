import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d  # Fonction pour la 3D
#import numpy as np

# Tableau pour les 3 axes
X = []
Y = []
Z = []
with open('res.txt','r') as file:
    for line in file.readlines():
        t = line.split(';')
        X.append(float(t[0]))
        Y.append(float(t[1]))
        Z.append(float(t[2].replace("\n","")))

# Tracé du résultat en 3D
fig = plt.figure()
ax = fig.gca(projection='3d')  # Affichage en 3D
ax.scatter(X, Y, Z)  # Tracé filaire
plt.title("Tracé filaire")
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.tight_layout()
plt.show()
