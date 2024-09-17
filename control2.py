import socket
import pygame


DEADZONE = 0.1

# Rover details
ROVER_IP = '192.168.1.100'  # Replace with the actual IP address of rover
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
    print(f"Sent packet: {packet}")

def apply_deadzone(value):
    """Apply a deadzone to joystick input.""" 
    return value if abs(value) > DEADZONE else 0

def get_pwm_drive_input(joystick=None):
    """Get PWM values for driving based on joystick input.""" 
    left_wheel_pwm = [128, 128, 128]
    right_wheel_pwm = [128, 128, 128]

    if joystick:
        forward_backward = apply_deadzone(joystick.get_axis(1))
        left_right = apply_deadzone(joystick.get_axis(0))

        if forward_backward < -DEADZONE:
            left_wheel_pwm = [255, 255, 255]
            right_wheel_pwm = [255, 255, 255]
        elif forward_backward > DEADZONE:
            left_wheel_pwm = [0, 0, 0]
            right_wheel_pwm = [0, 0, 0]

        if left_right < -DEADZONE:
            left_wheel_pwm = [0, 0, 0]
            right_wheel_pwm = [255, 255, 255]
        elif left_right > DEADZONE:
            left_wheel_pwm = [255, 255, 255]
            right_wheel_pwm = [0, 0, 0]

    return left_wheel_pwm, right_wheel_pwm

def get_pwm_arm_input(joystick=None):
    """Get PWM values for the arm based on joystick input.""" 
    # Default PWM values
    shoulder_pwm = 128
    wristright_pwm = 128
    wristleft_pwm = 128
    claw_pwm = 128
    gantry_pwm = 128
    elbow_pwm = 128

    if joystick: #WORKS
        # Update PWM values based on joystick input
        if joystick.get_button(0): 
            claw_pwm = 255 #x opens claw
        elif joystick.get_button(1): 
            claw_pwm = 0  #o closes claw

        if joystick.get_button(2):
            shoulder_pwm = 255  #square shoulder clockwise
        elif joystick.get_button(3):
             #triangle shoulder anticlockwise
            shoulder_pwm = 0   

        if joystick.get_button(4): 
              noop() #share
            
        elif joystick.get_button(5):
         noop() #ps

        if joystick.get_button(6):
          noop() #options
        elif joystick.get_button(7):
           noop()
        if joystick.get_button(8):
           noop()
        elif joystick.get_button(9):
            noop()

        if joystick.get_button(10):
            noop()
            # right up left down moves claw up (direction pad UP)
        elif joystick.get_button(11):
            wristright_pwm = 255
            wristleft_pwm = 0
             # right down left up moves claw DOWN (direction pad DOWN)
        if joystick.get_button(12):
            wristright_pwm = 0
            wristleft_pwm = 255
# right and left both reverse claw spins anticlockwise (direction pad LEFT)
        elif joystick.get_button(13):
            wristright_pwm = 0
            wristleft_pwm = 0
            # right and left both forward claw spins clockwise (direction pad RIGHT)
        if joystick.get_button(14):
            wristright_pwm = 255
            wristleft_pwm = 255








        gantry_pwm = 255 if joystick.get_axis(3) < -DEADZONE else 0 if joystick.get_axis(3) > DEADZONE else 128 #WORKS
        elbow_pwm = 255 if joystick.get_axis(2) < -DEADZONE else 0 if joystick.get_axis(2) > DEADZONE else 128 #WORKS

    return shoulder_pwm, wristright_pwm, wristleft_pwm, claw_pwm, gantry_pwm, elbow_pwm

def main():
    """Main function to run the rover control application.""" 
    running = True
    joystick = check_joystick()
    if joystick:
        display_message("Joystick Connected")
    else:
        display_message("No Joystick Connected")

    clock = pygame.time.Clock()

    prev_left_wheel_pwm = [128, 128, 128]
    prev_right_wheel_pwm = [128, 128, 128]

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

            left_wheel_pwm, right_wheel_pwm = get_pwm_drive_input(joystick)
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
