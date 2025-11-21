import sys
import os 
# NEW: Import tempfile for creating temporary input files
import tempfile
from pwn import * 

# --- Global Fuzz Target and Input File Path ---
TARGET_PATH = "./binaries/jpg1"
# Using the specific path confirmed by the user
INPUT_FILE_PATH = "example_inputs/jpg1.txt"

def test_io_path():
    """
    Reads a known-good JPEG, writes it to a temporary file, and runs the 
    target binary with the temporary file path as a command-line argument.
    This is often the necessary approach for image processing binaries.
    """
    # 1. Read the original file
    try:
        with open(INPUT_FILE_PATH, 'rb') as f:
            original_bytes = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE_PATH}' not found. Please check the path.", file=sys.stderr)
        sys.exit(1)
        
    print(f"[*] Starting test with {len(original_bytes)} bytes of data from {INPUT_FILE_PATH}...")
    
    # 2. Write the input data to a temporary file
    # 'delete=True' ensures the file is removed when the 'with' block exits.
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp:
        tmp.write(original_bytes)
        tmp.flush() # Ensure all data is written to disk
        
        temp_filename = tmp.name
        
        print(f"[*] Input saved to temporary file: {temp_filename}")
        
        # 3. Start the target process, passing the filename as an argument
        try:
            # We pass the filename as a list argument to the process command.
            # stdin=0 is used because the binary should read the file from the path, not stdin.
            p = process([TARGET_PATH, temp_filename], stdin=0, stdout=1, stderr=1, level='error')
            
            # --- ERROR HANDLING BLOCK ---
            try:
                # 4. Gather all output from stdout and stderr.
                output = p.recvall(timeout=1)
                
                # Wait for the program to terminate and get the exit code
                p.wait_for_close()
                exit_code = p.poll()
                
                print(f"[*] Target exited with code: {exit_code}")
                
                if output:
                    # The binary wrote something to stdout/stderr.
                    print("--- Target Output ---")
                    # Decode the output, ignoring errors, to see the message
                    output_text = output.decode(errors='ignore').strip()
                    print(output_text)
                    print("---------------------")
                elif exit_code != 0:
                     print("[!] Target exited with non-zero code but no output. Likely a silent crash.")
                else:
                    print("[*] Target processed input and exited cleanly (Exit Code 0).")

            except EOFError:
                # Catches unexpected process death during execution
                print("[!] Target process terminated unexpectedly (EOFError/Crash during execution).")
            
            # 5. Ensure the process is fully closed
            finally:
                if p.connected:
                    p.close()
                
        except OSError as e:
            # Handle cases where the binary itself cannot be executed
            print(f"Error executing target binary '{TARGET_PATH}': {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    test_io_path()
