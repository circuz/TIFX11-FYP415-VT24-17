import numpy as np
def sweep(robot):
    # Funktionen sveper den närliggande miljön.
    # Svepningen kan göras alltid i höger riktning.
    # Alltid åt höger då robotarna skall följa höger trafik
    # Retunera en matris med fermonnivåerna och vinklen/tiden att nå den riktningen
    # Svepnings funktionen jobbar i en röd-grön-vit skala
    # där röd är hög koncentration och vit är låg koncentration
    
    # Feromon matrisen med n stycken data punkter
    n = 36  # Motsvaraa  ungefär 10 graders intervall
    tau = np.zeros((n,2), dtype=float)

    # Sveper över intervallet
    for i in range(n):
        # Läser av ljuset. 
#        #Simulerar som ran random funktion
#        light = np.zeros(3, dtype=int)
#        # Intensiteten röd är ej intressant då den ej varierar
#        light[1] = np.random.randint(0,2*65535)
#        if light[1] > 65535:
#            light[1] = 65535
#            light[2] = np.random.randint(0,2*65535)-65535
#            if light[2] < 0:
#                light[2] = 0
#        conc = sum(light)
        tau[i] = np.array(([i, conc]))
    return tau


T = sweep(5)
print(T)

