import socket
from picarx import Picarx
from time import sleep

def start_follower():
    follower = Picarx()

    # Set up the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.1.30', 12345))  # Replace with the leader's IP address

    try:
        while True:
            # Receive data from the leader
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            
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

            # Introduce a delay based on the leader's speed
            sleep(0.1)  # Adjust the loop frequency as necessary

    except KeyboardInterrupt:
        print("Follower stopping...")
    finally:
        follower.stop()
        client_socket.close()

if __name__ == "__main__":
    start_follower()