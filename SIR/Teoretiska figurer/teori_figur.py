import matplotlib as mpl 
# mpl.use('pgf')

import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-v0_8')
from scipy.integrate import solve_ivp

# Parameters
beta = 0.7 / 10  # transmission rate
nu = 1 / 3  # recovery rate
N = 30  # total population

# Initial conditions
S0 = 27
I0 = 2
R0 = 0

# Time span
t = np.linspace(0, 10, 1000) 

# The SIR model differential equations.
def sir_model(t, y):
    S, I, R = y
    dSdt = -beta * S * I
    dIdt = beta * S * I - nu * I
    dRdt = nu * I
    return [dSdt, dIdt, dRdt]

# Initial conditions vector
y0 = [S0, I0, R0]

# Integrate the SIR equations over the time grid, t.
sol = solve_ivp(sir_model, [min(t), max(t)], y0, t_eval=t)

# Plot the data
plt.plot(sol.t, sol.y[0], 'b', label='Mottagliga')
plt.plot(sol.t, sol.y[1], 'r', label='Infekterade')
plt.plot(sol.t, sol.y[2], 'g', label='Återställda')
plt.title(f"SIR-simulering med $\\beta$ = {round(beta,1)} och $\\nu$ = {round(nu,1)}")
plt.xlabel('Tid (Minuter)')
plt.ylabel('Antal individer')
plt.legend()
plt.show()
# plt.savefig("sir_teori.pgf")
