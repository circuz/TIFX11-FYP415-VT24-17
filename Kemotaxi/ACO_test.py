import time
import numpy  as np
start_time = time.time()
p = 1
a = np.random.choice([True, False], p=[p, 1-p])
print(a)
