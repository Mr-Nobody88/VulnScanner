import subprocess
import os
import platform
import time
from tqdm import tqdm

def get_system_info():
    try:
        system_info = {}
        system_info['System'] = platform.system()
        system_info['Node Name'] = platform.node()
        system_info['Release'] = platform.release()
        system_info['Version'] = platform.version()
        system_info['Machine'] = platform.machine()
        system_info['Processor'] = platform.processor()

        # Memory and disk info
        system_info['Memory (GB)'] = round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024. ** 3), 2)
        system_info['Disk (GB)'] = round(float(subprocess.check_output('df / --output=size | tail -1', shell=True).decode('utf-8').strip()) / (1024. ** 3), 2)

        # CPU info (Cores and logical CPUs)
        cpu_info = subprocess.check_output("nproc", shell=True).decode("utf-8").strip()
        system_info['CPU Cores'] = cpu_info
        system_info['Logical CPUs'] = cpu_info

        return system_info
    except Exception as e:
        print(f"Error retrieving system information: {e}")

def run_command_with_loading_bar(command, description):
    try:
        print(f"{description}...")
        start_time = time.time()

        # Start the command in a subprocess
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check if process takes longer than 2 seconds, and if so, show the loading bar
        while process.poll() is None:  # Process is still running
            if time.time() - start_time > 2:
                for _ in tqdm(range(100), desc=description, ncols=100):  # Adding a loading bar
                    time.sleep(0.02)  # Simulating progress for the bar

        # Collect the output and error
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print(stdout)
        else:
            print(f"Error: {stderr}")

    except Exception as e:
        print(f"Error running command: {e}")

def run_nmap_vuln_scan(target):
    run_command_with_loading_bar(['nmap', '--script', 'vuln', target], 'Running nmap vulnerability scan')

def run_lynis_scan(mode):
    # Based on the selected mode, run the appropriate Lynis scan
    if mode == 'normal':
        run_command_with_loading_bar(['sudo', 'lynis', 'audit', 'system'], 'Running lynis audit in Normal mode')
    elif mode == 'forensics':
        run_command_with_loading_bar(['sudo', 'lynis', 'audit', 'system', '--forensics'], 'Running lynis audit in Forensics mode')
    elif mode == 'integration':
        run_command_with_loading_bar(['sudo', 'lynis', 'audit', 'system', '--integration'], 'Running lynis audit in Integration mode')
    elif mode == 'pentest':
        run_command_with_loading_bar(['sudo', 'lynis', 'audit', 'system', '--pentest'], 'Running lynis audit in Pentest mode')

def check_for_security_patches():
    run_command_with_loading_bar(['sudo', 'apt', 'list', '--upgradable'], 'Checking for missing security patches')

def main():
    # Get system info
    system_info = get_system_info()
    if system_info:
        print("\n--- System Information ---")
        for key, value in system_info.items():
            print(f"{key}: {value}")

    # Ask user to select Lynis scan mode
    print("\nSelect scan mode:")
    print("1. Normal [V]")
    print("2. Forensics [ ]")
    print("3. Integration [ ]")
    print("4. Pentest [ ]")

    mode_choice = input("Enter the number corresponding to the scan mode: ").strip()

    # Validate input and set mode
    if mode_choice == '1':
        mode = 'normal'
    elif mode_choice == '2':
        mode = 'forensics'
    elif mode_choice == '3':
        mode = 'integration'
    elif mode_choice == '4':
        mode = 'pentest'
    else:
        print("Invalid selection. Defaulting to Normal mode.")
        mode = 'normal'

    # Run vulnerability checks based on the system OS
    target = "127.0.0.1"  # You can change this to a remote IP address if needed

    # Only run nmap and lynis if it's a Linux system
    if system_info and system_info['System'] == 'Linux':
        # Run nmap vulnerability scan
        run_nmap_vuln_scan(target)

        # Run lynis audit based on user-selected mode
        run_lynis_scan(mode)

        # Check for missing security patches
        check_for_security_patches()

if __name__ == "__main__":
    main()