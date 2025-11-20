import glob
# Custom imports/defined classes
from fuzzer import Fuzzer
import sys
fuzzer = Fuzzer()


def main():
    # Fuzz each file in the 'binaries' folder
    # For each binary file, also get their respective input file from 'example_inputs'
    fuzzer.reset_output_dir()
    binaries_list = glob.glob("./binaries/*")
    error_dict = {}
    print(binaries_list)
    for binary in binaries_list:
        binary_name = binary.replace('./binaries/', '')
        binary_name = binary_name.replace('./binaries\\', '')
        progress = binaries_list.index(binary) + 1
        total = len(binaries_list)
        percentage = (progress / total) * 100
        print(" " * 160, end="\r", flush=True)  # Clear the line
        print(f"Running fuzzer against {binary_name}...                              ({percentage:.2f}%)[{binary}]", end="\r", flush=True)
        # start_time = time.time()
        # while True:
        #     elapsed = int(time.time() - start_time)
        #     print(f"Running fuzzer against {binary_name}... ({percentage:.2f}%)[{binary}] | Elapsed: {elapsed}s", end="\r", flush=True)
        #     # Break the loop if auto_test is done (simulate with a flag)
        #     # You may need to modify auto_test to support this, but for now, just run once per binary
        #     break
        found_error = fuzzer.auto_test(binary_name, 5000)
        error_dict[binary_name] = found_error
        # print(f"Finished running fuzzer against {binary_name}!                      ", end="\r", flush=True)

    print("Fuzzing complete!")
    print("Final report:")
    for binary, error in error_dict.items():
        print(f"{binary}:\n{error}")

if "__main__" == __name__:
    main()