import subprocess
import time
from scapy.all import AsyncSniffer, wrpcap
import os
import logging
import paramiko

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def remove_host_key(host):
    """Remove existing host key from known_hosts using ssh-keygen."""
    try:
        result = subprocess.run(["ssh-keygen", "-R", host], capture_output=True, text=True)
        if result.returncode == 0:
            logging.debug(f"Successfully removed existing host key for {host}")
        else:
            logging.error(f"Failed to remove existing host key for {host}: {result.stderr}")
    except Exception as e:
        logging.error(f"Error removing host key for {host}: {e}")

def add_host_key(host, user, password):
    """Add host key to known_hosts using paramiko."""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, password=password)
        key = client.get_transport().get_remote_server_key()
        client.close()
        
        # Write key to known_hosts file
        known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
        with open(known_hosts_path, 'a') as known_hosts_file:
            known_hosts_file.write(f"{host} {key.get_name()} {key.get_base64()}\n")
        
        logging.debug(f"Successfully added host key for {host}")
    except Exception as e:
        logging.error(f"Failed to add host key for {host}: {e}")

def run_ansible_playbook(playbook, inventory, iteration, task_name):
    # Ensure the playbook exists
    if not os.path.exists(playbook):
        logging.error(f"Playbook {playbook} does not exist.")
        return {
            "run": iteration,
            "task": task_name,
            "duration": 0,
            "num_packets": 0,
            "file_size": 0,
            "data_size": 0,
            "data_byte_rate": 0,
            "data_bit_rate": 0,
            "avg_packet_size": 0,
            "avg_packet_rate": 0,
            "error": f"Playbook {playbook} does not exist."
        }

    # Start packet sniffing
    logging.debug(f"Starting packet sniffing for {task_name} iteration {iteration}")
    sniffer = AsyncSniffer()
    sniffer.start()

    start_time = time.time()

    logging.debug(f"Running Ansible playbook {playbook} for {task_name} iteration {iteration}")
    result = subprocess.run(
        ["ansible-playbook", "-i", inventory, playbook],
        capture_output=True,
        text=True,
        env={**os.environ, "ANSIBLE_CONFIG": os.path.join(os.getcwd(), "ansible.cfg")}
    )

    end_time = time.time()
    duration = end_time - start_time

    # Stop packet sniffing
    packets = sniffer.stop()
    pcap_file = f"{task_name}_packets_{iteration}.pcap"
    wrpcap(pcap_file, packets)
    logging.debug(f"Packet sniffing stopped for {task_name} iteration {iteration}")

    num_packets = len(packets)
    file_size = os.path.getsize(pcap_file) / 1024  # in KB
    data_size = sum(len(pkt) for pkt in packets) / 1024  # in KB
    data_byte_rate = data_size / duration if duration > 0 else 0  # in KBps
    data_bit_rate = data_byte_rate * 8  # in kbps
    avg_packet_size = (data_size * 1024) / num_packets if num_packets > 0 else 0  # in bytes
    avg_packet_rate = num_packets / duration if duration > 0 else 0  # in packets/s

    logging.debug(f"Iteration {iteration} completed in {duration:.2f} seconds")
    logging.debug(f"STDOUT: {result.stdout}")
    logging.debug(f"STDERR: {result.stderr}")

    return {
        "run": iteration,
        "task": task_name,
        "duration": duration,
        "num_packets": num_packets,
        "file_size": file_size,
        "data_size": data_size,
        "data_byte_rate": data_byte_rate,
        "data_bit_rate": data_bit_rate,
        "avg_packet_size": avg_packet_size,
        "avg_packet_rate": avg_packet_rate
    }

if __name__ == "__main__":
    playbook = "playbook.yml"
    inventory = "hosts.ini"
    task_name = "ansible"

    # Remove and then add host keys for all routers
    for i in range(11, 15):
        if i == 12:
            continue
        host = f"192.168.21.{i}"
        remove_host_key(host)
        add_host_key(host, "karlis", "cisco")
    
    stats = []
    
    for i in range(1, 11):  # Run just one iteration for debugging
        logging.debug(f"Ansible Run {i}")
        stat = run_ansible_playbook(playbook, inventory, i, task_name)
        stats.append(stat)
    
    logging.debug("Ansible Stats: %s", stats)
    print("Ansible Stats:", stats)
