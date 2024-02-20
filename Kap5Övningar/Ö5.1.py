import numpy as np
import random as rd
import networkx as nx
import matplotlib.pyplot as plt
import Kap5Funk as k5f

## --- Exercise 15.1 ---
G = nx.Graph()  # Generera graf ytan.

size = 10    # Hur stor skall matrisen vara

# Generera anslutningsmatrisen M
M = np.zeros((size,size), dtype=int) # Noll matris
for i in range(size):   # Rad nummer
    for j in range(0,i):# Kolumn nummer
        M[i][j] = rd.randint(0,1)   # Slumpa tal 0 eller 1
        M[j][i] = M[i][j]   # Gör matrisen symetrisk
        if M[i][j] == 1:
            G.add_edge(i,j) # Skapar vägen mellan de två punkterna

pos = nx.spring_layout(G)   # Ger varje punkt en koordinat

# Ritar och visar grafen.
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=500, edge_color='k', linewidths=1, font_size=15)
plt.show()

# Generera avstånds matrisen D och vikt matrisen W
D = M.copy()    # Avstånds matrisen
D = D.astype(np.float32)
W = np.zeros((size,size), dtype=float) # Vikt matrisen
for i in range(size):
    for j in range(0,i):
        D[i][j] = D[i][j]*rd.randrange(10,100,10)
        D[j][i] = D[i][j]   # Gör matrisen symetrisk
        if D[i][j] != 0:    # Om 0 skall vikten vara 0 vilket betyder oändligheten
            W[i][j] = 1/D[i][j]
            W[j][i] = W[i][j]

# Generera Kemotaxi spåret
F = np.zeros((size,size), dtype=float) # Noll matris

A = k5f.RandomWalk(M,2,20)
print(A)
L = k5f.WalkLength(A,D)
print(L)
A = k5f.WalkSimp(A)
print(A)
print(k5f.WalkLength(A,D))
A = k5f.WalkSimp(A)
print(A)
print(k5f.WalkLength(A,D))
A = k5f.WalkSimp(A)
print(A)
print(k5f.WalkLength(A,D))



