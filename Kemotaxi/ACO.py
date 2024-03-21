import numpy as np
import asyncio

def sweep(robot, direction_right ):
    # Funktionen sveper den närliggande miljön.
    # Svepningen kan göras i vänster eller höger riktning
    # Retunera en matris med fermonnivåerna och vinklen/tiden att nå den riktningen
    
    # Feromon matrisen med n stycken data punkter
    n = 36  # Motsvaraa  ungefär 10 graders intervall
    tau = np.zeros((2,n), dtype=float)

    # Sveper över intervallet
    if direction_right: # Om svepningen skall ske i höger riktning
        for i in n:
            print(i)
    else:
        for i in n:
            print(i)


async def run(robot):
    


    # Always place a sleep at the end of the loop, this way the
    # microcontroller is allowed some time for other tasks
    await asyncio.sleep(0.1)