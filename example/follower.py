import socket
from picarx import Picarx
from time import sleep

def start_follower():
    follower = Picarx()

    # Set up the client to connect to AWS
    aws_ip = '18.116.43.113'  # Replace with your EC2 public IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to relay at {aws_ip}:12346...")
    client_socket.connect((aws_ip, 12346))
    print("Connected to relay")

    # Last received command
    last_command = 'f'  # Default to stopped

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
                
                # Only update the command if it's different or None
                if key != last_command:
                    last_command = key
                    
                    # Control follower based on the received key
                    if key == 'w':
                        follower.set_dir_servo_angle(0)
                        follower.forward(80)
                    elif key == 's':
                        follower.set_dir_servo_angle(0)
                        follower.backward(80)
                    elif key == 'a':
                        follower.set_dir_servo_angle(-30)
                        follower.forward(80)
                    elif key == 'd':
                        follower.set_dir_servo_angle(30)
                        follower.forward(80)
                    elif key == 'f' or key == 'None':
                        follower.stop()
                        
            except Exception as e:
                print(f"Error processing data: {e}")
                follower.stop()  # Safety measure: stop on error

            # Match the control loop frequency of the leader
            sleep(0.1)

    except KeyboardInterrupt:
        print("Follower stopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        follower.stop()
        client_socket.close()

if __name__ == "__main__":
    start_follower()