import subprocess
import time
import json
import random
import re
import os
import logging
from scapy.all import AsyncSniffer, wrpcap

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_ip_range():
    ip_base = f"192.168.{random.randint(0, 255)}.0"
    wildcard_mask = "0.0.255.255"
    acl_name = f"TEST_ACL_{random.randint(1, 1000)}"
    return ip_base, wildcard_mask, acl_name

def run_playbook(playbook, ip_range, wildcard_mask, acl_name, interface, inventory, iteration, task_name):
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
    sniffer = AsyncSniffer(iface=interface)
    sniffer.start()

    start_time = time.time()

    logging.debug(f"Running Ansible playbook {playbook} for {task_name} iteration {iteration}")
    result = subprocess.run(
        [
            "ansible-playbook",
            "-i", inventory,
            playbook,
            "-e", f"ip_range={ip_range}",
            "-e", f"wildcard_mask={wildcard_mask}",
            "-e", f"acl_name={acl_name}"
        ],
        capture_output=True,
        text=True
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

    # Extract warnings and errors
    warnings = re.findall(r"\[WARNING\]: (.+)", result.stderr)
    errors = re.findall(r"\[ERROR\]: (.+)", result.stderr)

    if result.returncode != 0:
        logging.error(f"Playbook {playbook} failed for {task_name} iteration {iteration}")
        logging.error(f"STDERR: {result.stderr}")
        error_msg = result.stderr
    else:
        logging.debug(f"Iteration {iteration} completed in {duration:.2f} seconds")
        logging.debug(f"STDOUT: {result.stdout}")
        error_msg = None

    if warnings:
        for warning in warnings:
            logging.warning(warning)

    if errors:
        for error in errors:
            logging.error(error)

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
        "avg_packet_rate": avg_packet_rate,
        "error": error_msg,
        "warnings": warnings,
        "errors": errors
    }

def verify_configurations(inventory):
    verify_playbook = "verify_configurations.yml"
    if not os.path.exists(verify_playbook):
        logging.error(f"Verification playbook {verify_playbook} does not exist.")
        return "Verification playbook does not exist."

    logging.debug(f"Running Ansible playbook {verify_playbook} to verify configurations")
    result = subprocess.run(
        ["ansible-playbook", "-i", inventory, verify_playbook],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        logging.error(f"Verification playbook {verify_playbook} failed")
        logging.error(f"STDERR: {result.stderr}")
        return result.stderr
    else:
        logging.debug(f"Verification playbook {verify_playbook} completed successfully")
        logging.debug(f"STDOUT: {result.stdout}")
        return result.stdout

def main():
    interface = "ens33"
    inventory = "hosts.ini"
    configure_playbook = "configure_network.yml"
    revert_playbook = "revert_network.yml"
    connectivity_check = subprocess.run(
        ["ansible", "-i", inventory, "all", "-m", "ping"],
        capture_output=True,
        text=True
    )
    logging.debug("Connectivity check result:")
    logging.debug(connectivity_check.stdout)
    results = []
    for i in range(10):
        ip_range, wildcard_mask, acl_name = generate_ip_range()
        configure_stats = run_playbook(configure_playbook, ip_range, wildcard_mask, acl_name, interface, inventory, i+1, "configure")
        revert_stats = run_playbook(revert_playbook, ip_range, wildcard_mask, acl_name, interface, inventory, i+1, "revert")
        results.append({
            "run": i + 1,
            "ip_range": ip_range,
            "wildcard_mask": wildcard_mask,
            "acl_name": acl_name,
            "configure": configure_stats,
            "revert": revert_stats
        })
        logging.debug(f"Run {i+1}: Configure - Duration={configure_stats['duration']:.2f}s, Network Packets Sent={configure_stats['num_packets']}")
        logging.debug(f"Run {i+1}: Revert - Duration={revert_stats['duration']:.2f}s, Network Packets Sent={revert_stats['num_packets']}")

    verification_output = verify_configurations(inventory)
    logging.debug(f"Verification Output: {verification_output}")

    with open("results.json", "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
