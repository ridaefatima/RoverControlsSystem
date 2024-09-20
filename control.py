import socket
import pygame

DEADZONE = 0.1

# Rover details
ROVER_IP = ''  # Replace with the actual IP address of rover  192.168.1.100
ROVER_PORT = 12345  # Replace with the actual PORT of rover

# Initialize socket
rover_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Rover Control")
pygame.joystick.init()

def check_joystick():
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        return joystick
    return None

def display_message(message):
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(200, 150))
    screen.blit(text, text_rect)
    pygame.display.flip()

def create_drive_packet(right_wheel_pwms, left_wheel_pwms):
    return f"D_{right_wheel_pwms[0]}_{right_wheel_pwms[1]}_{right_wheel_pwms[2]}_{left_wheel_pwms[0]}_{left_wheel_pwms[1]}_{left_wheel_pwms[2]}"

def create_arm_packet(shoulder_pwm, wristright_pwm, wristleft_pwm, claw_pwm, gantry_pwm, elbow_pwm):
    return f"A_{elbow_pwm}_{wristright_pwm}_{wristleft_pwm}_{claw_pwm}_{gantry_pwm}_{shoulder_pwm}"

def send_packet(packet):
    rover_socket.sendto(packet.encode('utf-8'), (ROVER_IP, ROVER_PORT))
    print(f"Sent packet: {packet}")

def apply_deadzone(value):
    return value if abs(value) > DEADZONE else 0

def get_pwm_drive_input(joystick=None):
    keys = pygame.key.get_pressed()

    left_wheel_pwm = [128, 128, 128]
    right_wheel_pwm = [128, 128, 128]

    if keys[pygame.K_UP]:
        left_wheel_pwm = [255, 255, 255]
        right_wheel_pwm = [255, 255, 255]
    elif keys[pygame.K_DOWN]:
        left_wheel_pwm = [0, 0, 0]
        right_wheel_pwm = [0, 0, 0]

    if keys[pygame.K_LEFT]:
        left_wheel_pwm = [0, 0, 0]
        right_wheel_pwm = [255, 255, 255]
    elif keys[pygame.K_RIGHT]:
        left_wheel_pwm = [255, 255, 255]
        right_wheel_pwm = [0, 0, 0]

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
    keys = pygame.key.get_pressed()

    shoulder_pwm = 128
    wristright_pwm = 128
    wristleft_pwm = 128
    claw_pwm = 128
    gantry_pwm = 128
    elbow_pwm = 128

    if keys[pygame.K_w]:
        gantry_pwm = 255
    elif keys[pygame.K_s]:
        gantry_pwm = 0

    if keys[pygame.K_a]:
        claw_pwm = 255
    elif keys[pygame.K_d]:
        claw_pwm = 0

    if keys[pygame.K_e]:
        elbow_pwm = 255
    elif keys[pygame.K_q]:
        elbow_pwm = 0

    if keys[pygame.K_v]:
        wristright_pwm = 255
    elif keys[pygame.K_b]:
        wristright_pwm = 0

    if keys[pygame.K_z]:
        wristleft_pwm = 255
    elif keys[pygame.K_x]:
        wristleft_pwm = 0

    if keys[pygame.K_g]:
        shoulder_pwm = 255
    elif keys[pygame.K_h]:
        shoulder_pwm = 0

    if joystick:
        if joystick.get_button(0):
            claw_pwm = 255
        elif joystick.get_button(1):
            claw_pwm = 0

        if joystick.get_button(2):
            shoulder_pwm = 255
        elif joystick.get_button(3):
            shoulder_pwm = 0

        if joystick.get_button(4):
            wristleft_pwm = 255
        elif joystick.get_button(5):
            wristright_pwm = 255

        if joystick.get_button(6):
            wristleft_pwm = 0
        elif joystick.get_button(7):
            wristright_pwm = 0

        gantry_pwm = 255 if joystick.get_axis(5) < -DEADZONE else 0 if joystick.get_axis(5) > DEADZONE else 128
        elbow_pwm = 255 if joystick.get_axis(4) < -DEADZONE else 0 if joystick.get_axis(4) > DEADZONE else 128

    return shoulder_pwm, wristright_pwm, wristleft_pwm, claw_pwm, gantry_pwm, elbow_pwm

def main():
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
                if event.type == pygame.JOYAXISMOTION:
                    print(f"Joystick axis motion: {event.axis} = {event.value}")
                if event.type == pygame.JOYBUTTONDOWN:
                    print(f"Joystick button down: {event.button}")
                if event.type == pygame.JOYBUTTONUP:
                    print(f"Joystick button up: {event.button}")

            left_wheel_pwm, right_wheel_pwm = get_pwm_drive_input()
            if left_wheel_pwm != prev_left_wheel_pwm or right_wheel_pwm != prev_right_wheel_pwm:
                drive_packet = create_drive_packet(right_wheel_pwm, left_wheel_pwm)
                send_packet(drive_packet)
                prev_left_wheel_pwm = left_wheel_pwm
                prev_right_wheel_pwm = right_wheel_pwm

            shoulder_pwm, wristright_pwm, wristleft_pwm, claw_pwm, gantry_pwm, elbow_pwm = get_pwm_arm_input()
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

    pygame.quit()

if __name__ == "__main__":
    main()
