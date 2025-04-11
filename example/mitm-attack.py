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
        
def start_mitm():
    # Connect to the leader
    leader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("MITM connecting to leader...")
    try:
        leader_socket.connect(('192.168.1.30', 12345))  # Connect to leader's IP and port
        print("Connected to leader")
    except Exception as e:
        print(f"Failed to connect to leader: {e}")
        return
    
    # Accept connection from the follower
    follower_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    follower_server.bind(('0.0.0.0', 12346))
    follower_server.listen(1)
    print("MITM waiting for follower connection...")
    
    follower_conn, follower_addr = follower_server.accept()
    print(f"Follower connected from {follower_addr}")
    
    # Start thread to handle communication from leader to follower
    threading.Thread(target=handle_leader_to_follower, args=(leader_socket, follower_conn)).start()
    
    # No need for follower to leader communication in this setup
    # since the leader is not expecting input from the follower

if __name__ == "__main__":
    start_mitm()