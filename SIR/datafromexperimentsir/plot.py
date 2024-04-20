import matplotlib.pyplot as plt

import os
print(os.getcwd())


# Get initial values
SIR = [2e9, [0,0,0]]
messages = {}
for filename in os.listdir(os.getcwd()):
    if filename[-3:] == '.py': # Skip python files
        continue
    with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
        initial = eval(f.readlines(1)[0])
        if initial["time"] < SIR[0]:
            SIR[0] = initial["time"]
        if initial["message"].endswith("S!"):
            SIR[1][0] += 1
        elif initial["message"].endswith("I!"):
            SIR[1][1] += 1
        elif initial["message"].endswith("R!"):
            SIR[1][2] += 1

        msgs = f.readlines()
        evaled_msgs = [eval(msg) for msg in msgs]
        print(evaled_msgs)
        for evaled_msg in evaled_msgs:
            # Dicts are sorted by default since python 3.7
            messages[evaled_msg["time"]] = evaled_msg["message"]

print(SIR)
print(messages)
print("===========")

plot_data = ([SIR[0]], [tuple(SIR[1])])
             
for time in messages.keys():
    msg = messages[time]
    if "I once was" in msg:
        newstats = list(plot_data[1][-1])
        newstats["SIR".index(msg[11])] -= 1
        newstats["SIR".index(msg[25])] += 1
        plot_data[0].append(time)
        plot_data[1].append(tuple(newstats))

print(plot_data)
plt.plot(plot_data[0], plot_data[1])
plt.show()
    