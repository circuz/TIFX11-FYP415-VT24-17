import numpy as np
import random as rd
import math
import matplotlib.pyplot as plt
from matplotlib.pylab import draw
from scipy.spatial import Delaunay

# Skapar en slumpmässig vandring, där inga kretsar finns. Tar ej hänsyn till fermoner
def RandomWalk(M, startingPoint, nrSteps):
    K = np.zeros((nrSteps), dtype=int)  # Hörnen som vi gått igenom
    K[0] = startingPoint
    
    for i in range(1, nrSteps):
        while True:
            j = rd.randrange(0,len(M[startingPoint]-1))     # Generera ett slumpmässigt hörn
            if j != K[i-1]:                              # Kontrollera så att det inte är samma hörn
                if M[K[i-1]][j] == 1:        # Kontrollera så att det finns en kant till hörnet
                    K[i] = j                 # Sparar hörnet till vägen
                    break
    return K

# Beräknar hur långt en myra har gått
def WalkLength(P, D):
    L = 0
    for i in range(len(P)-1):
        L = L + D[P[i]][P[i+1]]
    return L

# Förenkla vandringen, om samma hörn påträffats två gånger tas hörnen emellan bort.
# Tar i första hand bort det som gör vandringen mist.
def WalkSimp(P):
    a = len(P)
    d = np.array((0,0,0))   # Biggest diff
    Q = np.zeros((a, 3),dtype=int)
    for i in range(len(P)):
        for j in range(i+1,len(P)):
            if P[i] == P[j]:
                Q[i][0] = i
                Q[i][1] = j
                Q[i][2] = j-i
                if j-i > d[2]:
                    d = Q[i]   
    else:
        P = np.concatenate((P[0:d[0]],P[d[1]:len(P)]))
        return P
    
# Summan i nämnaren till ekv 15.2
def sumWeightPheromon(F, W, i, alpha, beta):
    sum = 0
    n = len(W[0])
    for j in range(n):
        sum = sum + F[i,j]**alpha*W[i,j]**beta  # Den totala sannolikheten att gå någon riktning från hörn i
    return sum

# Skapar ett nätverk byggt på Delaunay trianglar
def delaunayNätverk(n, avstånd):
    # Skapa slumpmässiga punkter
    points = np.random.rand(n, 2)*avstånd
    # Skapa Delaunay-nätverk
    tri = Delaunay(points)  # Ett delaunay nät består av kanter som aldrig omsluter ett hörn (kanterna bildar trianglar) 

    # Rita trianglarna
    plt.triplot(points[:,0], points[:,1], tri.simplices.copy())

    # Rita punkterna med numreringarna
    plt.plot(points[:,0], points[:,1], 'o')
    for i in range(len(points.transpose()[0])):
        plt.text(points[i][0], points[i][1], f' {i}', fontsize=12, color='black')
    fig = plt.show(block = False)

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
                ydiff = points[i][1]-points[j][1]
                D[i,j] = math.sqrt(xdiff**2 + ydiff**2)
                D[j,i] = D[i,j]
                W[i,j] = 1/D[i,j]
                W[j,i] = W[i,j]

    return M, W, D, fig

# Generera sannolikheten att vandra en kant från ett hörn
# Ö 15.6
def branchDecision(F, W, alpha, beta):
    n = len(W[0])
    p = np.zeros((n,n), dtype=float)
    for i in range(n):
        sum = sumWeightPheromon(F,W,i,alpha,beta)   # Få summa av sannolikhet att gå någon väg
        for j in range(n):
            p[i,j] = F[i,j]**alpha*W[i,j]**beta / sum   # Ekv. från bok
    return p

# Väljer den högst sannolika kanten att gå
# Ö 15.6
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

# Väljer en kant slumpmässigt men vägd med sannolikhets matrisen, endast 1 myra åt gången
def chooseBranchRand(P,p):
    li = np.array(range(0,len(p[0])), dtype=int)
    for i in range(1,len(P)):
        draw = np.random.choice(li, 1, True, p[P[i-1]])
            # if draw == P[i-1]:
            #     draw = chooseBranchRand(P,p)
    return draw[0]
    


# Prövnings matris
M = np.array([[0, 1, 1, 1, 1],
              [1, 0, 1, 0, 0],
              [1, 1, 0, 0, 1],
              [1, 0, 0, 0, 1],
              [1, 0, 1, 1, 0]])
D = np.array([[ 0., 80., 60., 50., 60.],
              [80.,  0., 40.,  0.,  0.],
              [60., 40.,  0.,  0., 90.],
              [50.,  0.,  0.,  0., 70.],
              [60.,  0., 90., 70.,  0.]])
T1 = np.array([1,2,3,4], dtype=int)
T2 = np.array([1,2,3,5,6,2,4,5,3], dtype=int)
#     0   1    2   3   4   5  6   7
p = [[0, 0.2, 0.5, 0, 0.1, 0, 0, 0.2],
     [0, 0.2, 0.5, 0, 0.1, 0, 0, 0.2],
     [0, 0.2, 0.5, 0, 0.1, 0, 0, 0.2],
     [0, 0.2, 0.5, 0, 0.1, 0, 0, 0.2],
     [0, 0.2, 0.5, 0, 0.1, 0, 0, 0.2],
     [0, 0.2, 0.5, 0, 0.1, 0, 0, 0.2],
     [0, 0.2, 0.5, 0, 0.1, 0, 0, 0.2],
     [0, 0.2, 0.5, 0, 0.1, 0, 0, 0.2]]

P = np.ones((1,8),dtype=int)[0]*-1

P[0] = 2

S = np.zeros((len(p[0])), dtype=int)
