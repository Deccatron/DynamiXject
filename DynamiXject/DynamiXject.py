import warnings
from cryptography.utils import CryptographyDeprecationWarning
import paramiko
import socket
import requests  # To fetch external IP address

warnings.filterwarnings(action='ignore', category=CryptographyDeprecationWarning)

def print_banner():
    print(r'''
________                                   .__ ____  ___     __                 __   
\______ \  ___.__.  ____  _____     _____  |__|\   \/  /    |__|  ____   ____ _/  |_ 
 |    |  \<   |  | /    \ \__  \   /     \ |  | \     /     |  |_/ __ \_/ ___\\   __\ 
 |       \\___  ||   |  \ / __ \_|  Y Y  \|  | /     \     |  |\  ___/\  \___ |  |  
/_______  // ____||___|  /(____  /|__|_|  /|__|/___/\  \/\__|  | \___  >\___  >|__|  
        \/ \/          \/      \/       \/           \_/\______|     \/     \/
''')

def get_external_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()  # Raise an error for bad responses
        external_ip = response.json().get('ip')
        return external_ip
    except requests.RequestException as e:
        print(f"Error fetching external IP: {e}")
        return None

def connect_ssh(hostname, port, username, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {hostname}:{port} as {username}")
        client.connect(hostname, port, username, password)
        print(f"Connection to {hostname} successful.")
        
        while True:
            # Prompt for a command to execute
            command = input(f"{username}@{hostname}:{port} $ ")
            if command.lower() in ['exit', 'quit']:
                break
            stdin, stdout, stderr = client.exec_command(command)
            print(stdout.read().decode(), end='')
            error = stderr.read().decode()
            if error:
                print(f"Error: {error}", end='')
        
        client.close()
        print(f"Connection to {hostname} closed.")
    
    except paramiko.AuthenticationException:
        print(f"Authentication failed for {hostname}.")
    except paramiko.SSHException as sshException:
        print(f"Unable to establish SSH connection to {hostname}: {sshException}")
    except socket.error as sockError:
        print(f"Socket error while connecting to {hostname}: {sockError}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def check_ssh_port(hostname, port):
    try:
        with socket.create_connection((hostname, port), timeout=5) as sock:
            print(f"SSH port {port} is open on {hostname}.")
            return True
    except (socket.timeout, ConnectionRefusedError):
        print(f"No open SSH port found on {hostname}:{port}.")
        return False
    except socket.error as e:
        print(f"Socket error while checking port {port} on {hostname}: {e}")
        return False

if __name__ == "__main__":
    print_banner()

    external_ip = get_external_ip()
    if external_ip:
        print(f"External IP to connect to: {external_ip}")
        
        username = "admin"
        password = "admin"
        ssh_port = 22

        if check_ssh_port(external_ip, ssh_port):
            connect_ssh(external_ip, ssh_port, username, password)
        else:
            print(f"Error: No open SSH port to connect to on {external_ip}.")
    else:
        print("Failed to retrieve the external IP address.")
