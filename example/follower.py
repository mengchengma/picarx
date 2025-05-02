import socket
from picarx import Picarx
import time

def start_follower():
    follower = Picarx()

    # Set up the client to connect to AWS
    aws_ip = '3.16.51.104'  # Replace with your EC2 public IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to relay at {aws_ip}:12346...")
    client_socket.connect((aws_ip, 12346))
    print("Connected to relay")

    try:
        while True:
            # Receive data from the relay
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print("Connection lost")
                break
            
            print(f"Received: {data}")
            try:
                # Process movement commands
                if ',' in data:  # Standard movement command
                    leader_speed, key = data.split(',')
                    leader_speed = int(leader_speed)

                    # Control follower based on the received key
                    if 'w' == key:
                        follower.set_dir_servo_angle(0)
                        follower.forward(leader_speed)
                    elif 's' == key:
                        follower.set_dir_servo_angle(0)
                        follower.backward(leader_speed)
                    elif 'a' == key:
                        follower.set_dir_servo_angle(-30)
                        follower.forward(leader_speed)
                    elif 'd' == key:
                        follower.set_dir_servo_angle(30)
                        follower.forward(leader_speed)
                    elif key == 'f':
                        follower.stop()
            except Exception as e:
                print(f"Error processing data: {e}")

            # Short sleep to control loop frequency
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("Follower stopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        follower.stop()
        client_socket.close()
        print("Follower stopped.")

if __name__ == "__main__":
    start_follower()