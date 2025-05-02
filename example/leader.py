import socket
import threading
import time
import termios
import tty
import sys
from picarx import Picarx

class KeyController:
    def __init__(self):
        self.key_pressed = None
        self.running = True
        self.lock = threading.Lock()
    
    def get_key(self):
        with self.lock:
            return self.key_pressed
    
    def set_key(self, key):
        with self.lock:
            self.key_pressed = key
    
    def is_running(self):
        with self.lock:
            return self.running
    
    def stop(self):
        with self.lock:
            self.running = False

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def key_reader(controller):
    print("Key reader started. Press keys to control the robot.")
    print("Controls: w,a,s,d for movement, f to stop, t to toggle attack mode, q to quit")
    
    while controller.is_running():
        key = getch().lower()
        controller.set_key(key)
        
        if key == 'q':
            controller.stop()
            break

def start_leader():
    leader = Picarx()
    leader_speed = 80  # Default speed
    attack_mode = False  # Attack mode starts disabled
    
    # Set up the controller for key presses
    controller = KeyController()
    
    # Start the key reading thread
    key_thread = threading.Thread(target=key_reader, args=(controller,))
    key_thread.daemon = True
    key_thread.start()

    # Set up the client to connect to AWS
    aws_ip = '3.16.51.104'  # Replace with your EC2 public IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to relay at {aws_ip}:12345...")
    client_socket.connect((aws_ip, 12345))
    print("Connected to relay server")

    try:
        last_key = None
        
        while controller.is_running():
            # Get the current key state
            key = controller.get_key()
            
            # Process key input
            if key is not None:
                # Handle toggle attack command
                if key == 't':
                    attack_mode = not attack_mode
                    status = "ENABLED" if attack_mode else "DISABLED"
                    print(f"Attack mode {status}")
                    # Send toggle command to server
                    toggle_cmd = f"TOGGLE_ATTACK"
                    client_socket.sendall(toggle_cmd.encode('utf-8'))
                    controller.set_key(None)  # Clear the key
                    continue
                
                # Handle movement keys
                if key == 'w':
                    leader.set_dir_servo_angle(0)
                    leader.forward(leader_speed)
                elif key == 's':
                    leader.set_dir_servo_angle(0)
                    leader.backward(leader_speed)
                elif key == 'a':
                    leader.set_dir_servo_angle(-30)
                    leader.forward(leader_speed)
                elif key == 'd':
                    leader.set_dir_servo_angle(30)
                    leader.forward(leader_speed)
                elif key == 'f':
                    leader.stop()
                elif key == 'q':
                    break
                
                # Only send if there's an actual movement key pressed
                if key in ['w', 'a', 's', 'd', 'f']:
                    # Send leader's speed and key pressed
                    data = f"{leader_speed},{key}"
                    client_socket.sendall(data.encode('utf-8'))
                    last_key = key
                
                # Clear the key after processing
                controller.set_key(None)
            else:
                # No key pressed, stop the car if it was moving
                if last_key in ['w', 'a', 's', 'd']:
                    leader.stop()
                    # Send stop command
                    data = f"{leader_speed},f"
                    client_socket.sendall(data.encode('utf-8'))
                    last_key = 'f'
            
            # Short sleep to control loop speed
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("Leader stopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        leader.stop()
        print("Leader stopped.")

if __name__ == "__main__":
    start_leader()