import socket
import pygame

DEADZONE = 0.1

# Rover details
ROVER_IP = '127.0.0.1'  # Replace with the actual IP ADDRESS of rover
ROVER_PORT = 12345  # Replace with the actual PORT of rover

# Initialize socket
rover_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Rover Control")
pygame.joystick.init()

# function used to ensure unnecessary buttons do not get main functionalities without messing up the rest of the code
def noop():
    """A no-op function that does nothing."""
    pass

def check_joystick():
    """Check if a joystick is connected.""" 
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        return joystick
    return None

def display_message(message):
    """Display a message on the screen.""" 
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(200, 150))
    screen.blit(text, text_rect)
    pygame.display.flip()

def create_drive_packet(right_wheel_pwms, left_wheel_pwms):
    """Create a packet for driving commands.""" 
    return f"D_{right_wheel_pwms[0]}_{right_wheel_pwms[1]}_{right_wheel_pwms[2]}_{left_wheel_pwms[0]}_{left_wheel_pwms[1]}_{left_wheel_pwms[2]}"

def create_arm_packet(shoulder_pwm, wristright_pwm, wristleft_pwm, claw_pwm, gantry_pwm, elbow_pwm):
    """Create a packet for arm commands.""" 
    return f"A_{elbow_pwm}_{wristright_pwm}_{wristleft_pwm}_{claw_pwm}_{gantry_pwm}_{shoulder_pwm}"

def send_packet(packet):
    """Send a packet to the rover.""" 
    rover_socket.sendto(packet.encode('utf-8'), (ROVER_IP, ROVER_PORT))
    print(f"{packet}")

def apply_deadzone(value):
    """Apply a deadzone to joystick input.""" 
    return value if abs(value) > DEADZONE else 0

def get_pwm_drive_input(joystick=None, forward_speed=148, reverse_speed=108):
    """Get PWM values for driving based on joystick input.""" 
    left_wheel_pwm = [128, 128, 128]
    right_wheel_pwm = [128, 128, 128]

    if joystick:
        forward_backward = apply_deadzone(joystick.get_axis(1))
        left_right = apply_deadzone(joystick.get_axis(0))

        if forward_backward < -DEADZONE:
            left_wheel_pwm = [forward_speed, forward_speed, forward_speed]
            right_wheel_pwm = [forward_speed, forward_speed, forward_speed]
        elif forward_backward > DEADZONE:
            left_wheel_pwm = [reverse_speed, reverse_speed, reverse_speed]
            right_wheel_pwm = [reverse_speed, reverse_speed, reverse_speed]

        if left_right < -DEADZONE:
            # Turn left (reverse left wheel, forward right wheel)
            left_wheel_pwm = [reverse_speed, reverse_speed, reverse_speed]
            right_wheel_pwm = [forward_speed, forward_speed, forward_speed]
            # Turn right (forward left wheel, reverse right wheel)
        elif left_right > DEADZONE:
            left_wheel_pwm = [forward_speed, forward_speed, forward_speed]
            right_wheel_pwm = [reverse_speed, reverse_speed, reverse_speed]

    return left_wheel_pwm, right_wheel_pwm

def get_pwm_arm_input(joystick=None):
    """Get PWM values for the arm based on joystick input.""" 
    shoulder_pwm = 128
    wristright_pwm = 128
    wristleft_pwm = 128
    claw_pwm = 128
    gantry_pwm = 128
    elbow_pwm = 128

    if joystick:
        if joystick.get_button(0): 
            claw_pwm = 148  # A Opens claw
        elif joystick.get_button(1): 
            claw_pwm = 108  # B Closes claw

        if joystick.get_button(2):
            elbow_pwm = 148  #  X button moves elbow up
        elif joystick.get_button(3):
            elbow_pwm = 108  #  Y button moves elbow down

        hat = joystick.get_hat(0)  # Get Direction pad input
        if hat == (0, 1):  # UP direction on Direction Pad, moves gantry up
            wristright_pwm = 148
            wristleft_pwm = 108
        elif hat == (0, -1):  # DOWN direction on Direction Pad, moves gantry down
            wristright_pwm = 108
            wristleft_pwm = 148
        if hat == (-1, 0):  # LEFT direction on Direction Pad, 
            wristright_pwm = 108  #claw spins anticlockwise
            wristleft_pwm = 108
        if hat == (1, 0):  # RIGHT direction on Direction Pad
            wristright_pwm = 148  #  claw spins clockwise
            wristleft_pwm = 148

        gantry_pwm = 148 if joystick.get_axis(3) < -DEADZONE else 108 if joystick.get_axis(3) > DEADZONE else 128 #gantry up/down on y axis of joystick
        shoulder_pwm = 108 if joystick.get_axis(2) < -DEADZONE else 148 if joystick.get_axis(2) > DEADZONE else 128  # shoulder moves clockwise/anticlockwise on x axis of joystick

    return shoulder_pwm, wristright_pwm, wristleft_pwm, claw_pwm, gantry_pwm, elbow_pwm

#Shows is joystick is connected or not
def main():
    """Main function to run the rover control application."""
    running = True
    joystick = check_joystick()
    if joystick:
        display_message("Joystick Connected")
    else:
        display_message("No Joystick Connected")

    clock = pygame.time.Clock()

    # Initialize forward and reverse speed variables
    forward_speed = 148
    reverse_speed = 108
    button_4_pressed = False  # Track button 4 state
    button_5_pressed = False  # Track button 5 state

    prev_left_wheel_pwm = [128, 128, 128]
    prev_right_wheel_pwm = [128, 128, 128]

    # Initialize previous arm PWM values
    prev_shoulder_pwm = 128
    prev_wristright_pwm = 128
    prev_wristleft_pwm = 128
    prev_claw_pwm = 128
    prev_gantry_pwm = 128
    prev_elbow_pwm = 128

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if joystick:
                current_button_4_state = joystick.get_button(4)  # Get the current state of button 4
                current_button_5_state = joystick.get_button(5)  # Get the current state of button 5

                # Logic for button 4
                if current_button_4_state and not button_4_pressed:  # Button 4 pressed
                    # Increment forward speed by 20 and decrement reverse speed by 20
                    if forward_speed < 255:
                        forward_speed = min(255, forward_speed + 20)
                    if reverse_speed > 0:
                        reverse_speed = max(0, reverse_speed - 20)
                    button_4_pressed = True  #  button 4  pressed

                if not current_button_4_state:  # Button 4 released
                    button_4_pressed = False  # button 4  released

                # Logic for button 5
                if current_button_5_state and not button_5_pressed:  # Button 5 pressed
                    # Decrement forward speed by 20 and increment reverse speed by 20
                    if forward_speed > 148:
                        forward_speed = max(148, forward_speed - 20)
                    if reverse_speed < 108:
                        reverse_speed = min(108, reverse_speed + 20)
                    button_5_pressed = True  # Mark button 5 as pressed

                if not current_button_5_state:  # Button 5 released
                    button_5_pressed = False  # Mark button 5 as released

            # Decide the current speed based on joystick input
            left_wheel_pwm, right_wheel_pwm = get_pwm_drive_input(joystick, forward_speed, reverse_speed)
            if left_wheel_pwm != prev_left_wheel_pwm or right_wheel_pwm != prev_right_wheel_pwm:
                drive_packet = create_drive_packet(right_wheel_pwm, left_wheel_pwm)
                send_packet(drive_packet)
                prev_left_wheel_pwm = left_wheel_pwm
                prev_right_wheel_pwm = right_wheel_pwm

            shoulder_pwm, wristright_pwm, wristleft_pwm, claw_pwm, gantry_pwm, elbow_pwm = get_pwm_arm_input(joystick)
            if (shoulder_pwm != prev_shoulder_pwm or wristright_pwm != prev_wristright_pwm or 
                wristleft_pwm != prev_wristleft_pwm or claw_pwm != prev_claw_pwm or 
                gantry_pwm != prev_gantry_pwm or elbow_pwm != prev_elbow_pwm):
                arm_packet = create_arm_packet(shoulder_pwm, wristright_pwm, wristleft_pwm, claw_pwm, gantry_pwm, elbow_pwm)
                send_packet(arm_packet)
                prev_shoulder_pwm = shoulder_pwm
                prev_wristright_pwm = wristright_pwm
                prev_wristleft_pwm = wristleft_pwm
                prev_claw_pwm = claw_pwm
                prev_gantry_pwm = gantry_pwm
                prev_elbow_pwm = elbow_pwm

            clock.tick(30)

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        pygame.quit()

if __name__ == "__main__":
    main()

#im cooked