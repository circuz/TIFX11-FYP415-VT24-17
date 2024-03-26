# Here is an example of experiment code and the robot library

# Import libraries, asyncio is required to sleep
import asyncio


# The file should contain a async run function which takes the robot object as
# an argument. This function is ran at the start of the experiment, and should
# not exit for its duration. Keep in mind the robot might randomly reset because
# of power issues, in which case this function will be ran again.
#
# Remember that the function is async, which has special meaning in python. This
# means that some functions, like sleeping (using asyncio.sleep) and most robot
# functions need to be prefixed with the await keyword or they will not do
# anything.
# Example: "await asyncio.sleep(1)" to sleep for 1 second
async def run(robot):
    # Start with any initialization or things that should only run once. We will
    # start by making the robot move forwards for 5 seconds with its green light
    # on.

    # Sets the color of the coms LED to green. The coms LED is the one in the
    # middle of the robot under the cone, which is used for communication
    # between robots. The argument of the function is the color in
    # (red, green, blue) format, where each value is in the range 0-255.
    await robot.leds.set_coms((0, 255, 0))

    # Make the robot move forward. other functions are robot.motors.go_left,
    # robot.motors.go_right and robot.motors.stop.
    await robot.motors.go_forward()

    # Wait 5 seconds to let the robot move
    await asyncio.sleep(5)

    # Turn off the motors
    await robot.motors.stop()

    # Now lets make the robot move away from anything that is touching its
    # bumpers. To start, we need to make the bumpers output a signal so that
    # other robots can detect them
    #
    # The default value is None, which doesn't output any signal. True outputs a
    # high voltage level, and False outputs a low voltage level.
    robot.bumpers.drive_front = False
    robot.bumpers.drive_back = False
    robot.bumpers.drive_left = False
    robot.bumpers.drive_right = False

    # Now lets do the repeating part of the experiment. Create a while true loop
    # to keep the experiment running forever
    while True:
        # Detect if a bumper is touching anything using robot.bumpers.<direction>
        if robot.bumpers.back is False:
            await robot.motors.go_forward()
        elif robot.bumpers.left is False:
            await robot.motors.go_right()
        elif robot.bumpers.right is False:
            await robot.motors.go_left()
        else:
            await robot.motors.stop()

        # We could also have set the motors using robot.motors.set_left and
        # set_right, which takes the motor power an argument in the format of a
        # number between 0 and 1.
        #
        # For example, this code is equivalent to await robot.motors.go_left():
        # await robot.motors.set_left(0)
        # await robot.motors.set_right(1)

        # lastly, lets use the color sensors. The color that is detected from
        # the left sensor can be accessed using robot.color_sensors.left. This,
        # similarly to setting a led color is a tuple in the format (r, g, b),
        # however the values are 16-bit and thus range from 0 to 65535.
        #
        # Let's display the color that is detected by the left sensor on the
        # coms LED. To do this, we need to divide each color by 8 to convert the
        # 0-65535 range to 0-255.
        await robot.leds.set_coms(
            (
                robot.color_sensors.left[0] // 8,
                robot.color_sensors.left[1] // 8,
                robot.color_sensors.left[2] // 8,
            )
        )

        # Always place a sleep at the end of the loop, this way the
        # microcontroller is allowed some time for other tasks
        await asyncio.sleep(0.1)
