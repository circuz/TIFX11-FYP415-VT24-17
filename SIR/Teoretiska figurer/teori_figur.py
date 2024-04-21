import matplotlib as mpl 
# mpl.use('pgf')

import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-v0_8')
from scipy.integrate import solve_ivp

# Parameters
beta = 0.7 / 30  # transmission rate
nu = 1 / 5  # recovery rate
N = 30  # total population

# Initial conditions
S0 = 25
I0 = 5
R0 = 0

# Time span
t = np.linspace(0, 40, 1000)  # From day 0 to day 40

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
plt.title('SIR Modellen')
plt.xlabel('Dagar')
plt.ylabel('Antal individer')
plt.legend()
plt.show()
