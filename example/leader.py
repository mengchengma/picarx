import socket
from picarx import Picarx
from time import sleep
import readchar

def start_leader():
    leader = Picarx()
    leader_speed = 50  # Default speed

    # Set up the client to connect to AWS
    aws_ip = '18.221.242.132'  # Replace with your EC2 public IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to relay at {aws_ip}:12345...")
    client_socket.connect((aws_ip, 12345))
    print("Connected to relay server")

    try:
        while True:
            # User control for direction
            key = readchar.readkey().lower()
            
            if 'w' == key:
                leader.set_dir_servo_angle(0)
                leader.forward(80)
            elif 's' == key:
                leader.set_dir_servo_angle(0)
                leader.backward(80)
            elif 'a' == key:
                leader.set_dir_servo_angle(-30)
                leader.forward(80)
            elif 'd' == key:
                leader.set_dir_servo_angle(30)
                leader.forward(80)
            elif key == 'f':
                leader.stop()  # Stop the vehicle
            elif key == 'q':
                break  # Exit the loop

            # Send leader's speed and key pressed
            data = f"{leader_speed},{key}"
            client_socket.sendall(data.encode('utf-8'))
            sleep(0.1)  # Adjust the frequency of sending data

    except KeyboardInterrupt:
        print("Leader stopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        leader.stop()

if __name__ == "__main__":
    start_leader()