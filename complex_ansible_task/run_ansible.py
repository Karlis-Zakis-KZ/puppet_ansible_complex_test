import subprocess
import time
import os
import logging
import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run_ansible_playbook(playbook, inventory, iteration, task_name):
    # Ensure the playbook exists
    if not os.path.exists(playbook):
        logging.error(f"Playbook {playbook} does not exist.")
        return {
            "run": iteration,
            "task": task_name,
            "duration": 0,
            "stdout": "",
            "stderr": "",
            "error": f"Playbook {playbook} does not exist."
        }

    # Start packet sniffing
    logging.debug(f"Starting packet sniffing for {task_name} iteration {iteration}")
    start_time = time.time()

    logging.debug(f"Running Ansible playbook {playbook} for {task_name} iteration {iteration}")

    # Set environment variable to disable SSH host key checking
    env = os.environ.copy()
    env["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    # Include timestamp in environment variables
    env["ANSIBLE_DATE_TIME"] = datetime.datetime.now().isoformat()

    result = subprocess.run(
        ["ansible-playbook", "-i", inventory, playbook],
        capture_output=True,
        text=True,
        env=env
    )

    end_time = time.time()
    duration = end_time - start_time

    logging.debug(f"Iteration {iteration} completed in {duration:.2f} seconds")
    logging.debug(f"STDOUT: {result.stdout}")
    logging.debug(f"STDERR: {result.stderr}")

    return {
        "run": iteration,
        "task": task_name,
        "duration": duration,
        "stdout": result.stdout,
        "stderr": result.stderr
    }

if __name__ == "__main__":
    apply_playbook = "apply_compliance.yml"
    inventory = "hosts.ini"

    stats = []

    for i in range(1, 11):  # Run a few iterations to test
        logging.debug(f"Ansible Run {i}")
        stat = run_ansible_playbook(apply_playbook, inventory, f"run_{i}", "apply_compliance")
        stats.append(stat)

    logging.debug("Ansible Stats: %s", stats)
    print("Ansible Stats:", stats)
