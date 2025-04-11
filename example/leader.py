import socket
from picarx import Picarx
from time import sleep
import readchar

def start_leader():
    leader = Picarx()
    leader_speed = 50  # Default speed

    # Set up the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12346))  # Listen on all interfaces on port 12345
    server_socket.listen(1)
    print("Leader is waiting for a connection...")

    conn, addr = server_socket.accept()
    print(f"Connection established with {addr}")

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
            conn.sendall(data.encode('utf-8'))
            sleep(0.1)  # Adjust the frequency of sending data

    except KeyboardInterrupt:
        print("Leader stopping...")
    finally:
        conn.close()
        server_socket.close()
        leader.stop()

if __name__ == "__main__":
    start_leader() 