import socket
import pygame

# Rover details
ROVER_IP = '192.168.1.100'  # Replace with the actual IP address of rover, currently a mock rover IP
ROVER_PORT = 12345  # Replace with the actual PORT of rover, currently a mock rover PORT

# Initialize socket
rover_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize pygame for both the keyboard and joystick input
pygame.init()
screen = pygame.display.set_mode((400, 300))

# Joystick initialization
pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Function that creates the drive packet
def create_drive_packet(right_wheel_pwms, left_wheel_pwms):
    #this is the ORDER that the drive packet will be printed in.
    return f"D_{right_wheel_pwms[0]}_{right_wheel_pwms[1]}_{right_wheel_pwms[2]}_{left_wheel_pwms[0]}_{left_wheel_pwms[1]}_{left_wheel_pwms[2]}"

# Function that creates the arm packet
def create_arm_packet(shoulder_pwm, wristright_pwm, wristleft_pwm, claw_pwm, gantry_pwm, elbow_pwm):
    #this is the ORDER that the arm packet will be printed in.
    return f"A_{elbow_pwm}_{wristright_pwm}_{wristleft_pwm}_{claw_pwm}_{gantry_pwm}_{shoulder_pwm}"

# Function that sends the packets to the rover
def send_packet(packet):
    rover_socket.sendto(packet.encode('utf-8'), (ROVER_IP, ROVER_PORT))
    
    print(f"Sent packet: {packet}") # prints all the packets

# Function to handle key/joystick inputs for drive
def get_pwm_drive_input():
    keys = pygame.key.get_pressed()

    #Define the default PWM values for wheels. 128 is neutral position. 
    left_wheel_pwm = [128, 128, 128]
    right_wheel_pwm = [128, 128, 128]

    # Handle the keyboard input for the drive
    if keys[pygame.K_UP]: # moves all wheels forward
        left_wheel_pwm = [255, 255, 255]
        right_wheel_pwm = [255, 255, 255]
    elif keys[pygame.K_DOWN]: # moves all wheels backwards
        left_wheel_pwm = [0, 0, 0]
        right_wheel_pwm = [0, 0, 0]
    
    if keys[pygame.K_LEFT]: # allows for a left turn by moving left and right wheels in opposite directions
        left_wheel_pwm = [0, 0, 0] #left wheels turn backwards
        right_wheel_pwm = [255, 255, 255] # right wheels turn forward allowing a left turn
    elif keys[pygame.K_RIGHT]:# allows for a right turn by moving left and right wheels in opposite directions
        left_wheel_pwm = [255, 255, 255] # left wheels turn forward allowing for a right turn
        right_wheel_pwm = [0, 0, 0] # right wheels turn backwards

    # Handle joystick input for drive (axis 1 (y-axis) for forward/backward, axis 0 (x-axis) for left/right)
    if pygame.joystick.get_count() > 0:
        forward_backward = joystick.get_axis(1)  # Forward/Backward axis
        left_right = joystick.get_axis(0)  # Left/Right axis


# -0.1 to 0.1 represents neutral/dead zone on joysticks. 
# Important note for self : pushing a joystick forward causes the Y axis value to be negative. So a value less than -0.1 would lead to forward movement of the rover.
        if forward_backward < -0.1:
            left_wheel_pwm = [255, 255, 255]
            right_wheel_pwm = [255, 255, 255]
#value greater than 0.1 (neutral) leads to backward movement of rover
        elif forward_backward > 0.1:
            left_wheel_pwm = [0, 0, 0]
            right_wheel_pwm = [0, 0, 0]
#value greater than 0.1 (neutral) leads to leftward movement of rover on x axis
        if left_right < -0.1:
            left_wheel_pwm = [0, 0, 0]
            right_wheel_pwm = [255, 255, 255]
#value less than 0.1 (neutral) leads to rightward movement of rover on x axis
        elif left_right > 0.1:
            left_wheel_pwm = [255, 255, 255]
            right_wheel_pwm = [0, 0, 0]

    return left_wheel_pwm, right_wheel_pwm

# Function that handles key/joystick inputs for the arm
def get_pwm_arm_input():
    keys = pygame.key.get_pressed()

    # Default PWM values (128 is neutral)
    shoulder_pwm = 128
    wristright_pwm = 128
    wristleft_pwm = 128
    claw_pwm = 128
    gantry_pwm = 128
    elbow_pwm = 128

    #  keyboard input for arm
    if keys[pygame.K_w]: # motor 1 in arm
        gantry_pwm = 255 # press W to move gantry up
    elif keys[pygame.K_s]:
        gantry_pwm = 0 # press S to move gantry down

    if keys[pygame.K_a]: # motor 2 in arm
        claw_pwm = 255 # press A to open claw
    elif keys[pygame.K_d]:
        claw_pwm = 0 # press D to close claw

    if keys[pygame.K_e]: #motor 3 in arm
        elbow_pwm = 255 # press E to move elbow up
    elif keys[pygame.K_q]: 
        elbow_pwm = 0 # press Q to move elbow down

    if keys[pygame.K_r]: # motor 4 in arm
        wristright_pwm = 255 # wrist left being neutral and wrist right being forward leads to clockwise motion
        wristleft_pwm = 128 #press R to move clockwise
    elif keys[pygame.K_f]: # motor 5 in arm
        wristright_pwm = 128 #wrist right being neutral and wrist left being forward leads to counterclockwise motion
        wristleft_pwm = 255 #press F to move counterclockwise

    if keys[pygame.K_g]: # motor 6 in arm
        shoulder_pwm = 255 #press G to spin shoulder clockwise 
    elif keys[pygame.K_h]:
        shoulder_pwm = 0 #press H to spin shoulder counterclockwise 

    # Handle joystick input for arm (example: buttons control movement)
    if pygame.joystick.get_count() > 0:
        # Note: currently dont have a controller so idk which button does what LOL
        if joystick.get_button(0):  # Press Button 0 to move gantry up
            gantry_pwm = 255 
        elif joystick.get_button(1):  # Press Button 1 to move gantry down
            gantry_pwm = 0

        if joystick.get_button(2):  # Press Button 2 to open claw
            claw_pwm = 255
        elif joystick.get_button(3):  # Press Button 3 to close claw
            claw_pwm = 0

    return shoulder_pwm, wristright_pwm, wristleft_pwm, claw_pwm, gantry_pwm, elbow_pwm

# Main function to control the rover with keyboard or controller
def main():
    running = True
    clock = pygame.time.Clock()

    # Initialize previous state variables for drive
    prev_left_wheel_pwm = [128, 128, 128]
    prev_right_wheel_pwm = [128, 128, 128]

    # Initialize previous state variables for arm
    prev_shoulder_pwm = 128
    prev_wristright_pwm = 128
    prev_wristleft_pwm = 128
    prev_claw_pwm = 128
    prev_gantry_pwm = 128
    prev_elbow_pwm = 128

    try:
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Get PWM values from input for drive
            left_wheel_pwm, right_wheel_pwm = get_pwm_drive_input()

            # Check if PWM values have changed for drive
            if left_wheel_pwm != prev_left_wheel_pwm or right_wheel_pwm != prev_right_wheel_pwm:
                drive_packet = create_drive_packet(right_wheel_pwm, left_wheel_pwm)
                send_packet(drive_packet)

                # Update previous PWM values
                prev_left_wheel_pwm = left_wheel_pwm
                prev_right_wheel_pwm = right_wheel_pwm

            # Get PWM values from input for arm
            shoulder_pwm, wristright_pwm, wristleft_pwm, claw_pwm, gantry_pwm, elbow_pwm = get_pwm_arm_input()

            # Check if PWM values have changed for arm
            if (shoulder_pwm != prev_shoulder_pwm or wristright_pwm != prev_wristright_pwm or 
                wristleft_pwm != prev_wristleft_pwm or claw_pwm != prev_claw_pwm or 
                gantry_pwm != prev_gantry_pwm or elbow_pwm != prev_elbow_pwm):
                arm_packet = create_arm_packet(shoulder_pwm, wristright_pwm, wristleft_pwm, claw_pwm, gantry_pwm, elbow_pwm)
                send_packet(arm_packet)

                # Update previous PWM values
                prev_shoulder_pwm = shoulder_pwm
                prev_wristright_pwm = wristright_pwm
                prev_wristleft_pwm = wristleft_pwm
                prev_claw_pwm = claw_pwm
                prev_gantry_pwm = gantry_pwm
                prev_elbow_pwm = elbow_pwm

            # Limit the loop to 30 FPS
            clock.tick(30)

    except KeyboardInterrupt:
        print("Exiting...")

    pygame.quit()

if __name__ == "__main__":
    main()
