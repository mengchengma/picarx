import socket
import threading

def handle_leader_to_follower(leader_conn, follower_conn):
    try:
        while True:
            data = leader_conn.recv(1024)
            if not data:
                print("Leader disconnected")
                break
            
            print(f"Leader → Follower: {data.decode('utf-8')}")
            follower_conn.sendall(data)
    except Exception as e:
        print(f"Leader-to-follower error: {e}")

def handle_follower_to_leader(follower_conn, leader_conn):
    try:
        while True:
            data = follower_conn.recv(1024)
            if not data:
                print("Follower disconnected")
                break
            
            print(f"Follower → Leader: {data.decode('utf-8')}")
            leader_conn.sendall(data)
    except Exception as e:
        print(f"Follower-to-leader error: {e}")

def start_mitm():
    # Create socket for the leader connection
    leader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    leader_socket.bind(('0.0.0.0', 12345))  # Listen for leader
    leader_socket.listen(1)
    print("MITM waiting for leader connection...")
    
    # Create socket for the follower connection
    follower_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    follower_socket.bind(('0.0.0.0', 12346))  # Listen for follower on different port
    follower_socket.listen(1)
    print("MITM waiting for follower connection...")
    
    # Accept connection from the leader
    leader_conn, leader_addr = leader_socket.accept()
    print(f"Leader connected from {leader_addr}")
    
    # Accept connection from the follower
    follower_conn, follower_addr = follower_socket.accept()
    print(f"Follower connected from {follower_addr}")

    # Start threads to handle bidirectional communication
    threading.Thread(target=handle_leader_to_follower, args=(leader_conn, follower_conn)).start()
    threading.Thread(target=handle_follower_to_leader, args=(follower_conn, leader_conn)).start()

if __name__ == "__main__":
    start_mitm()