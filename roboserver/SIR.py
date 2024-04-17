# Import libraries, asyncio is required to sleep
import asyncio


# The file should contain a async run function which takes the robot object as
# an argument. This function is ran at the start of the experiment, and should
# not exit for its duration. Keep in mind the robot might randomly reset because
# of power issues, in which case this function will be ran again.
async def run(robot):
    # Start with any initialization or things that should only run once. 

    ## Initialize SIR experiment
    try:
        about_me_file = open(r"about_me", "r")
        role = about_me_file.readlines()[0]
    except IOError:
        # If the about me file doesn't exist we create it.
        about_me_file = open(r"about_me", "w")
        about_me_file.write("S")
        role = "S"

    about_me_file.close()

    if role not in ("S", "I", "R"):
        role = "S"
    if role == "S": #Succeptible
        await robot.leds.set_coms((0, 0, 255))
        robot.bumpers.drive_front = False
        robot.bumpers.drive_back = False
        robot.bumpers.drive_left = False
        robot.bumpers.drive_right = False
    if role == "I": #Infected
        await robot.leds.set_coms((0, 255, 0))
        robot.bumpers.drive_front = True
        robot.bumpers.drive_back = True
        robot.bumpers.drive_left = True
        robot.bumpers.drive_right = True
    if role == "R": #Recovered
        await robot.leds.set_coms((255, 0, 0))
        robot.bumpers.drive_front = False
        robot.bumpers.drive_back = False
        robot.bumpers.drive_left = False
        robot.bumpers.drive_right = False

    # Now lets do the repeating part of the experiment. Create a while true loop
    # to keep the experiment running forever
    while True:
        
        # about_me should be on the form:
        # [S,I,R]
        # for example it could contain just the letter M if the robot is supposed to be m
        about_me_file = open(r"about_me", "r")
        role = about_me_file.readlines()[0]
        
        if role == "S": #Succeptible
            if (True in (robot.bumpers.back, robot.bumpers.front, robot.bumpers.left, robot.bumpers.right)):
                # Become infected
                about_me_file = open(r"about_me", "w")
                about_me_file.write("I")
                about_me_file.close()
                role = "I"
                await robot.leds.set_coms((0, 255, 0))
                robot.bumpers.drive_front = True
                robot.bumpers.drive_back = True
                robot.bumpers.drive_left = True
                robot.bumpers.drive_right = True
        elif role == "I": #Infected
            await robot.motors.go_forward()
        elif role == "R": #Recovered/Removed
            pass
        else:
            about_me_file = open(r"about_me", "r+")
            print(f"I don't know what my role is! My about me file says: {about_me_file.readlines()} and I'm just gonna turn red and remove myself now...")
            about_me_file.write("R")
            about_me_file.close()
            await robot.leds.set_coms((0, 255, 0))


        await asyncio.sleep(0.1)
