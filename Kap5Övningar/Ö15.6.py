import numpy as np
import Kap5Funk as k5f
import math
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

# Generera sannolikheten att vandra en kant från ett hörn
def branchDecision(F, W, alpha, beta):
    n = len(W[0])
    p = np.zeros((n,n), dtype=float)
    for i in range(n):
        sum = k5f.sumWeightPheromon(F,W,i,alpha,beta)   # Få summa av sannolikhet att gå någon väg
        for j in range(n):
            p[i,j] = F[i,j]**alpha*W[i,j]**beta / sum   # Ekv. från bok
    return p

# Väljer den högst sannolika kanten att gå
def chooseBranch(P, p):
    stat = np.array((0,-1),dtype=float) # Spara sannolikheten att gå till ett hörn
    for i in range(len(p[0])):          # Går igenom samtliga hörn som vi kan gå till 1, 2, 3 ...
        if i not in P:                  # Kollar så vi inte gå till ett hörn som vi redan varit vid
            if p[P[-1],i] > stat[0]:    # Kollar om kanten till hörn i har störst sannolikhet
                stat[0] = p[P[-1],i]    # Spara den högsta sannlikheten
                stat[1] = i             # Spara hörnet med högst sannolikhet
    if stat[1] == -1:                   # Ifall vi redan nått samtliga hörn eller kan inte komma till oanvänt hörn
        for i in range(len(p[0])):
            if i != P[-1] and i != P[-2]:   # Kontroller så vi inte gå till befintligt eller föregående hörn
                if p[P[-1],i] > stat[0]:    
                    stat[0] = p[P[-1],i]
                    stat[1] = i

    return np.append(P,int(stat[1]))

# Skapa ett formon spår
def enkeltFermonGenererign(M):
    F = M.copy()
    F = F.astype(float)
    for i in range(n):
        for j in range(n):
            if F[i,j] == 1:
                F[i,j] = np.random.random()*10
                F[j,i] = F[i,j]
    return F

n = 5

M, D, W, fig = k5f.delaunayNätverk(n, 10)

F = enkeltFermonGenererign(M)

p = branchDecision(F,W,0.9,1.1)

# Väljer en start punkt
P = np.array((np.random.randint(0,len(M)),),dtype=int)

# Skapar en vandring som är 2n lång
for i in range(2*n):
    P = chooseBranch(P, p)


# print(' --------- Anlustningsmatrisen --------- ')
# print(M)
# print(' --------- Avståndsmatrisen --------- ')
# print(D)
# print(' --------- Viktmatrisen --------- ')
# print(W)
# print(' --------- Fermonmatrisen --------- ')
# print(F)
print(' --------- Sannolikhets --------- ')
print(p)
print(' --------- Vandringsmatrisen --------- ')
print(P)
# plt.show(block = False)


