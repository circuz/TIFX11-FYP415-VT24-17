import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

# Antal punkter
n = 5

# Skapa slumpmässiga punkter
points = np.random.rand(n, 2)*10
# Skapa Delaunay-nätverk
tri = Delaunay(points)  # Ett delaunay nät består av kanter som aldrig omsluter ett hörn (kanterna bildar trianglar) 

# Rita trianglarna
plt.triplot(points[:,0], points[:,1], tri.simplices.copy())
# Rita punkterna med numreringarna
plt.plot(points[:,0], points[:,1], 'o')
for i in range(len(points.transpose()[0])):
    plt.text(points[i][0], points[i][1], f' {i}', fontsize=12, color='black')
plt.show(block=False)

M = np.zeros((n,n),dtype=int)
for triangle in tri.simplices.copy():   # Triangle beskriver trianglen där nr i matrisen är för vilket hörn som syns i figuren
    for i in range(3):
        start = triangle[i]             # Ta fram utgångshörnet
        end = triangle[(i+1)%3]         # ta fram hörnet där kanten slutar
        M[start, end] = 1               # Sparar kanten
        M[end, start] = M[start, end]

D = M.copy()
D = D.astype(float)
W = np.zeros((n,n),dtype=float)
for i in range(n):
    for j in range(n):
        if D[i,j] == 1:
            xdiff = points[i][0]-points[j][0]
            print(xdiff)
            ydiff = points[i][1]-points[j][1]
            print(ydiff)
            D[i,j] = math.sqrt(xdiff**2 + ydiff**2)
            D[j,i] = D[i,j]
            W[i,j] = 1/D[i,j]
            W[j,i] = W[i,j]


print('---Anslutningsmatrisen---')        
print(M)
print('---Avståndsmatrisen---')        
print(D)
print('---Viktmatrisen---')        
print(W)

plt.show()