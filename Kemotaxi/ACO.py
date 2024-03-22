import numpy as np
import asyncio

# Funktionerna som kommer användas under kemotaxi experimentet
def follow(robot):
    # Funktion som skall följa ljus stråket
    
    print('har följt')

def trail_decision(robot):
    # Funktionen som skall göra beslutet hurvida ljus spåret skall följas eller 
    # om ett befintligt skall fortsättas följas 

    print('har bestämt')
    
def colission(robot):
    # Funktion som hanterar eventuella kollisioner

    print('har kolliderat')

def goal(robot):
    # Funktion som hanterar vad som händer när målet har funnits
    # Kan utvecklas om tid och intresse finns

    print('hittat målet')

def direction_decision(robot):
    # Funktion som hanterar vilken riktning som roboten skall söka i

    print('har valt riktning')

def drive(robot):
    # Funktion om hanterar körningen

    print('har kört')

async def run(robot):
    


    # Always place a sleep at the end of the loop, this way the
    # microcontroller is allowed some time for other tasks
    await asyncio.sleep(0.1)