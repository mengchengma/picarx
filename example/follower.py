import socket
from picarx import Picarx
from time import sleep

def start_follower():
    follower = Picarx()

    # Set up the client to connect to AWS
    aws_ip = '3.145.196.198'  # Replace with your EC2 public IP
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
                leader_speed, key = data.split(',')
                leader_speed = int(leader_speed)

                # Control follower based on the received key
                if 'w' == key:
                    follower.set_dir_servo_angle(0)
                    follower.forward(80)
                elif 's' == key:
                    follower.set_dir_servo_angle(0)
                    follower.backward(80)
                elif 'a' == key:
                    follower.set_dir_servo_angle(-30)
                    follower.forward(80)
                elif 'd' == key:
                    follower.set_dir_servo_angle(30)
                    follower.forward(80)
                elif key == 'f':
                    follower.stop()
            except Exception as e:
                print(f"Error processing data: {e}")

            # Introduce a delay based on the leader's speed
            sleep(0.1)  # Adjust the loop frequency as necessary

    except KeyboardInterrupt:
        print("Follower stopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        follower.stop()
        client_socket.close()

if __name__ == "__main__":
    start_follower()