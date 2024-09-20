# RoverControlsSystem

submission for first training module; functional system for rover.

This is the README file for task 1 (Control System Task):

left joystick: controls drive packets sent (controls forward, reverse, left , and right motions at a speed of 0 for reverse 128 for neutral and 148 for forward)

LB and RB buttons are used to adjust speed, LB increments the speed of the drive packet motors by 20 each time it is pressed to maximum values of 255(forward motion) and 0(reverse motion), while RB decrements the speed of the drive backet by decrements of 20 till a minimum value of 148 (forward motion) and 108 (reverse motion) respectively.

right joystick: controls arm packets, y axis makes sure the gantry moves up and down while the x axis moves the shoulder clockwise and anticlockwise when the joystick is moved right or left respectively.

Buttons A and B are responsible for opening and closing the claw

Buttons X and Y are responsible for moving elbow up and down

In the Direction pad, the UP movement moves claw upward by wrist left and right spinning in opposite directions

In the Direction pad, the DOWN movement moves claw downward by wrist left and right spinning in opposite directions

In the Direction pad, the LEFT movement moves spins the claw anticlockwise by spinning wrist left and right in same direction

In the Direction pad, the RIGHT movement moves spins the claw clockwise by spinning wrist left and right in same direction
