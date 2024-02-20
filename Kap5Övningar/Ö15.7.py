import numpy as np
import Kap5Funk as k5f
import math
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

N = 40  # Storleken på nätet
A = 10  # Antalet myror
S = 80  # Max antal steg

s0 = 2  # Start punkt
f0 = 40 # Slut punkt
f0 = f0-1   # Eftersom vi räknar med nollan finns ej punkt f0

# Generera en vandringsmatris
P = np.ones((A,S),dtype=int)*-1  # Varje rad är en myra och varje kolumn är då hörnen som myran är/varit i
for i in range(len(P)):
    P[i,0] = s0

M, D, W, fig = k5f.delaunayNätverk(N, 10)

tau = M.copy()

alpha = 0.8
beta = 1.0
rho = 0.5

# Generera sannolikhets matrisen
p = k5f.branchDecision(tau, W, alpha, beta)

# Generera vandringsmatrisen för samtliga myror
for nr in range(len(P)):            # Valet av myra
    for step in range(1,len(P[0])): # Steg antalet in i processen
        while True: 
            P[nr,step] = k5f.chooseBranchRand(P[nr], p) # Ta fram steget som myran tar med hänsyn till sannolikheten/viktan slump
            if P[nr,step] != P[nr,step-1]:  # Kontrollera så att vi inte har kommit till samma punkt igen, Bör ej kunna ske dock
                break
        if P[nr,step] == f0:        # Myran har hittat slut destinationen
            print('kom i mål')
            break

# Ritar ut det första utksatet av en vandring
for nr in range(len(P)):                    # Vi kolla på myra (nr) och fäljer dess väg
    if P[nr,-1] == -1 or P[nr,-1] == f0:    # Kontrollera så att myra (nr) faktiskt kom till destinationen
        print(P[nr])


plt.show()
