import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d  # Fonction pour la 3D
import numpy as np

# Tableau pour les 3 axes
X = []
Y = []
Z = []
with open('res.txt','r') as file:
    for line in file.readlines():
        t = line.split(';')
        X.append(int(t[0]))
        Y.append(int(t[1]))
        Z.append(int(t[2]))

# Tracé du résultat en 3D
fig = plt.figure()
ax = fig.gca(projection='3d')  # Affichage en 3D
ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)  # Tracé filaire
plt.title("Tracé filaire")
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.tight_layout()
plt.show()