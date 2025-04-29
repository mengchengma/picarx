import socket
from picarx import Picarx
from time import sleep
import threading
import readchar

def start_leader():
    leader = Picarx()
    leader_speed = 50  # Default speed

    # Set up the client to connect to AWS
    aws_ip = '18.116.43.113'  # Replace with your EC2 public IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to relay at {aws_ip}:12345...")
    client_socket.connect((aws_ip, 12345))
    print("Connected to relay server")

    # Variable to store the currently pressed key
    current_key = None
    running = True

    # Function to continuously check for key presses
    def key_reader():
        nonlocal current_key, running
        while running:
            key = readchar.readkey().lower()
            # Update the current key
            if key in ['w', 'a', 's', 'd']:
                current_key = key
                print(f"Key pressed: {key}")
            elif key == 'f':
                current_key = 'f'  # Stop command
                print("Stopping")
            elif key == 'q':
                current_key = None
                running = False
                print("Quitting")
            
    # Start the key reading thread
    key_thread = threading.Thread(target=key_reader)
    key_thread.daemon = True
    key_thread.start()

    try:
        while running:
            # Process the current key state
            if current_key == 'w':
                leader.set_dir_servo_angle(0)
                leader.forward(80)
            elif current_key == 's':
                leader.set_dir_servo_angle(0)
                leader.backward(80)
            elif current_key == 'a':
                leader.set_dir_servo_angle(-30)
                leader.forward(80)
            elif current_key == 'd':
                leader.set_dir_servo_angle(30)
                leader.forward(80)
            elif current_key == 'f' or current_key is None:
                leader.stop()  # Stop the vehicle
            
            # Send leader's speed and current key state
            data = f"{leader_speed},{current_key if current_key else 'f'}"
            client_socket.sendall(data.encode('utf-8'))
            sleep(0.1)  # Control loop frequency

    except KeyboardInterrupt:
        print("Leader stopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        running = False
        client_socket.close()
        leader.stop()
        # Wait for key thread to finish
        key_thread.join(timeout=1.0)

if __name__ == "__main__":
    start_leader()