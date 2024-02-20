import numpy as np
import Kap5Funk as k5f
import math
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

N = 100  # Storleken på nätet
A = 20  # Antalet myror
S = 80  # Max antal steg

s0 = 0  # Start punkt
f0 = 70 # Slut punkt
f0 = f0-1   # Eftersom vi räknar med nollan finns ej punkt f0
alpha = 0.8
beta = 1.0
rho = 0.5
Q = 0.5

M, D, W, fig = k5f.delaunayNätverk(N, 10)

tau = M.copy()

for n in range(1000):
    # Generera en vandringsmatris och återställer den
    P = np.ones((A,S),dtype=int)*-1  # Varje rad är en myra och varje kolumn är då hörnen som myran är/varit i
    for i in range(A):
        P[i,0] = s0

    # Generera sannolikhets matrisen
    p = k5f.branchDecision(tau, W, alpha, beta)

    # Generera vandringsmatrisen för samtliga myror
    P = k5f.chooseBranchRand(s0,f0,P,p)

    # Hitta de myror som faktiskt nådde målet
    goodAnt = k5f.goodAnts(P, f0)

    # Beräkna längden varje myra vandrat
    length = np.zeros(A,dtype=float)
    for nr in goodAnt:
        length[nr] = k5f.WalkLength(P[nr],D)

    # Updatera formonspåret
    tau = k5f.updatePhermone(rho, Q, P, tau, goodAnt, length)

print(goodAnt)

print(length)

print(P[0])

plt.show()

