import numpy as np
import asyncio
import time

# Viktiga konstanter som kan vara intressanta att variera
    # step i drive
    # alpha i drive
    # step_alphai drive
    # omega i trail_decision
    # OMEGA i trail_decision
    # delta i follow
    # sigma i follow

# Kommentarer
    # Kemotaxi färg: Röd->Gult->Vit. Rött är högst konsentration, men är det minsta värde. Vit har minst koncentration, men högst värde
    # Mat färg: Blått
    # Hem färg: Grönt
    # I experimentet påbörjas finns inga feromoner i miljön

    # Funktionerna som kommer användas under kemotaxi experimentet
# Funktion som skall följa ljus stråket
async def follow(robot, omega, OMEGA, delta, sigma, step):
# Start tid
    start_time = time.time()  
# Följa ljus stråket åt höger eller vänster    
    go_left = np.random.choice([True, False])
# För att gå vänster    
    if go_left:
    # Påbörja en vandringen utmed stråket
        while start_time + step > time.time():
        # Feromon koncentrationen är högst i stråket
            light_high = sum(robot.color_sensors.left)
        # Rotera vänster tills feromon koncentrationen minskat med delta
            await robot.motors.go_left()
            while sum(robot.color_sensors.left) < light_high*(1+delta):
            # Undersöker om målet hittas
            # Om hemmet är målet
                if goal_home and (robot.color_sensors.left[1]>60000 and sum(robot.color_sensors.left)<70000):
                    await robot.motors.stop()
                    await goal(robot)
                    return False
            # Om maten är målet
                elif not goal_home and (robot.color_sensors.left[2]>60000 and sum(robot.color_sensors.left)<70000):
                    await robot.motors.stop()
                    await goal(robot)
                    return False
                await asyncio.sleep(0.1)
            await robot.motors.stop()
        # Feromon koncentrationen är lägst utanför stråket
            light_low = sum(robot.color_sensors.left)
        # Rotera höger tills feromon koncentrationen ökat med sigma
            await robot.motors.right()
            while sum(robot.color_sensors.left) > light_low*sigma:
                
                await asyncio.sleep(0.1)
        # Vandrat fram en period
            await robot.motors.stop()
            asyncio.sleep(0.1)
# För att gå åt höger istället
    else:
    # Feromon koncentrationen är högst i stråket
        light_high = sum(robot.color_sensors.left)
    # Går igenom stråket för att förflytta sig på rätt sida stråket (höger trafik), tills feromon koncentrationen minskat med delta
        await robot.motor.go_forward()
        while sum(robot.color_sensors.left) < light_high*(1+delta):
            await asyncio.sleep(0.1)
        await robot.motors.stop()
    # Feromon koncentrationen är lägst utanför stråket
        light_low = sum(robot.color_sensors.left)
    # Vandra in i stråket igen för att enkelt sluta och börja innuti stråket
        await robot.motors.right()
        while sum(robot.color_sensors.left) > light_low*sigma:
            await asyncio.sleep(0.1)
        await robot.motors.stop()
    # Feromon koncentrationen är högst i stråket
        light_high = sum(robot.color_sensors.left)
    # Påbörja en vandring utmed stråket (identiskt till att gå vänster)
        while start_time + step > time.time():
        # Feromon koncentrationen är högst i stråket
            light_high = sum(robot.color_sensors.left)
        # Rotera vänster tills feromon koncentrationen minskat med delta
            await robot.motors.go_left()
            while sum(robot.color_sensors.left) < light_high*(1+delta):
                await asyncio.sleep(0.1)
            await robot.motors.stop()
        # Feromon koncentrationen är lägst utanför stråket
            light_low = sum(robot.color_sensors.left)
        # Rotera höger tills feromon koncentrationen ökat med sigma
            await robot.motors.right()
            while sum(robot.color_sensors.left) > light_low*sigma:
                await asyncio.sleep(0.1)
        # Vandrat fram en period
            await robot.motors.stop()
            asyncio.sleep(0.1)

    return trail_decision(robot, True, light_high, omega, OMEGA)

# Funktionen som skall göra beslutet hurvida ljus spåret skall följas eller om ett befintligt skall fortsättas följas 
async def trail_decision(robot, follow_trail, light_intensity, omega, OMEGA):
# Beräkna feromonkoncentrationen
    tau = (196605-light_intensity)/131070
    if follow_trail:
        p = tau**OMEGA
    else:
        p = tau**omega
    follow_trail = np.random.choice([True, False], p=[p, 1-p])
    return follow_trail

# Funktion som hanterar eventuella kollisioner
async def colission(robot):
    rotation_time_col = 2
    await robot.motors.go_right()
    await asyncio.sleep(rotation_time_col)
    await robot.motors.stop()

# Funktion som hantera när ett mål hittas
async def goal(robot):
# Kan utvecklas om tid och intresse finns
# Lyser med dioden under några sekunder för att indekerar vad som har hittats
    # Om hemmet söktes
    if goal_home:
        for i in range(20):
            await robot.leds.set_coms((0, 255, 0))
            await asyncio.sleep(0.1)
            await robot.leds.set_coms((0, 0, 0))
            await asyncio.sleep(0.1)
    # Om målet söktes
    else:
        for i in range(20):
            await robot.leds.set_coms((0, 0, 255))
            await asyncio.sleep(0.1)
            await robot.leds.set_coms((0, 0, 0))
            await asyncio.sleep(0.1)        

    goal_home = not goal_home

# Funktion som hantera vilken riktning roboten skall köra i
async def direction_decision(robot):
# Hur länge roboten skall rotera
    rotation_time = np.random.random()*10/2
# Går rakt fram om tiden är under 1.5 sekund
    if rotation_time < 1.5:
        return
# Ta fram rotations riktningen slumpmässigt
    if np.random.randint(0,2) == 0:
        await robot.motors.go_left()
    else:
        await robot.motors.go_right()
    await asyncio.sleep(rotation_time)    
    
# Funktion om hanterar körningen
async def drive(robot, step, alpha, step_alpha, omega, OMEGA):
# Step är lambda
# alpha är hög felmarginal vi har till att detakerar ett feromonspår
# Initierar kollisions sensorerna för vänster, fram och höger
    robot.bumpers.drive_front = False
    robot.bumpers.drive_left = False
    robot.bumpers.drive_right = False
# Skapar matris för jämföra feromon intensitets skillnaden mellan två punkter:
# Om roboten är i hemmet eller maten sätts feromonnivån till minimum
    if (robot.color_sensors.left[1]>60000 and light<70000) or (robot.color_sensors.left[2]>60000 and light<70000):
        tau = [time.time(), 196605]
    else:
        tau = [time.time(), sum(robot.color_sensors.left)]
# Om feromonspår skall följas
    follow_trail = False
# Start motorn för att gå fram
    await robot.motors.go_forward()

    start_time = time.time()

    while start_time+step > time.time():
        # Ladda in ljus intensiteten
            light = sum(robot.color_sensors.left)

        # Undersöker om en kollision uppstår
            if robot.bumpers.drive_front or robot.bumpers.left or robot.bumpers.right:
                await robot.motors.stop()
                await colission(robot)
                await robot.motors.go_forward()

        # Undersöker om målet hittas
            # Om hemmet är målet
                if goal_home and (robot.color_sensors.left[1]>60000 and light<70000):
                    await robot.motors.stop()
                    await goal(robot)
                    break
            # Om maten är målet
                elif not goal_home and (robot.color_sensors.left[2]>60000 and light<70000):
                    await robot.motors.stop()
                    await goal(robot)
                    break

        # Undersöker förändring i feromon intensitets förändring
            # Kontrollera så vi inte är i hemmet eller målet
            if not ((robot.color_sensors.left[1]>60000 and light<70000) or (robot.color_sensors.left[2]>60000 and light<70000)):
                # Kontrollera så att ett tids steg har passerat
                if tau[0]+step_alpha < time.time():
                    # Undersöker om feromon nivån har ökat
                    if tau[1]/light >= (1+alpha):
                        await robot.motors.stop()
                        follow_trail = trail_decision(robot, follow_trail, light, omega, OMEGA)
                        asyncio.sleep(0.1)
                        break
                    tau = [time.time(), sum(robot.color_sensors.left)]
                
            await asyncio.sleep(0.1)
    
# Stanna roboten
    await robot.motors.stop()
    return follow_trail

# Funktion som kör roboten
async def run(robot):
# Initierar konstanter
    step = 10
    global goal_home
    goal_home = False
    alpha = 0.2
    step_alpha = 1
    omega = 0.8
    OMEGA = 0.7
    delta = 0.8
    sigma = 0.8
# Utköningen ur hemmet/målet
    await direction_decision(robot)
    follow_trail = await drive(robot, step, alpha, step_alpha, omega, OMEGA)

    while True:
        if follow_trail:
            follow_trail = await follow(robot, omega, OMEGA, delta, sigma, step)
        else:
            await direction_decision(robot)
            follow_trail = await drive(robot, step, alpha, step_alpha)
        
        await asyncio.sleep(0.1)




    # Always place a sleep at the end of the loop, this way the
    # microcontroller is allowed some time for other tasks
