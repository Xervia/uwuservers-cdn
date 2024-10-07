from time import sleep
import subprocess
import atexit
import sys
import os

# Paths and filenames
path = os.path.dirname(os.path.abspath(__file__)) 
main = "main.py"
data = "service.dat"
main_path = os.path.join(path, main)
data_path = os.path.join(path, data)

def get_content():
    """Reads the content of the data file."""
    try:
        with open(data_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""  # Return empty string if file does not exist

def clear_data_file():
    """Clears the data file by writing an empty string."""
    with open(data_path, "w+") as f:
        f.write("")

def safe_terminate_process(p):
    """Safely terminates and kills the subprocess."""
    if p.poll() is None:  # Check if the process is still running
        p.terminate()
        try:
            p.wait(timeout=5)  # Give it 5 seconds to terminate gracefully
        except subprocess.TimeoutExpired:
            p.kill()  # Force kill if it doesn't terminate in time

def on_exit(p):
    """Function to be executed on program exit."""
    safe_terminate_process(p)
    if os.path.exists(data_path):
        os.remove(data_path)  # Clean up the data file on exit

if __name__ == "__main__":
    run = True

    while run:
        clear_data_file()  # Clear the data file at the start

        try:
            # Start the subprocess for main.py
            p = subprocess.Popen(["python3", main_path])

            # Register cleanup function with atexit
            atexit.register(on_exit, p)

            # Monitor the subprocess and data file for 'restart' or 'exit'
            while p.poll() is None:
                content = get_content()
                if content == "restart":
                    safe_terminate_process(p)
                    clear_data_file()  # Clear the restart command after handling
                    # Restart logic: exit loop and restart
                    break
                elif content == "exit":
                    safe_terminate_process(p)
                    run = False  # Set flag to stop main loop
                    break

                sleep(1)  # Avoid busy waiting with a 1-second delay

        except Exception as e:
            print(f"An error occurred: {e}")
            run = False  # Exit if any error occurs

    # Clean up before exiting
    if os.path.exists(data_path):
        os.remove(data_path)
