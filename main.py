import glob
# Custom imports/defined classes
from fuzzer import Fuzzer
from textwrap import indent
fuzzer = Fuzzer()

def print_error_report(error_dict):
    for binary, error in error_dict.items():
        if not error or error == "No errors found":
            print(f"{binary}: No errors found\n")
            continue
        if isinstance(error, str):
            print(f"{binary}: {error}\n")
            continue
        if isinstance(error, dict):
            print(f"{binary}: Detected errors")
            for exit_code, entries in error.items():
                print(f"  Exit code: {exit_code}")

                for (stderr, stdout, elapsed, strategy) in entries:
                    print("    ─────────────────────────────")
                    print(f"    Strategy : {strategy}")
                    print(f"    Time     : {elapsed:.4f}s")
                    print(f"    Stderr   :\n      {stderr.strip() or '<empty>'}")
                    print(f"    Stdout   :\n      {stdout.strip() or '<empty>'}")

            print()
            continue

        print(f"{binary}: Unexpected error format: {type(error)}")
        print(f"  Value: {error}\n")



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
        print(f"Running fuzzer against {binary_name}...                                     ({percentage:.2f}%)[{binary}]", end="\r", flush=True)
        found_error = fuzzer.auto_test(binary_name, 10000)
        error_dict[binary_name] = found_error
        # print(f"Finished running fuzzer against {binary_name}!                      ", end="\r", flush=True)

    print("Fuzzing complete!")
    print("Final report:")
    print_error_report(error_dict)

if "__main__" == __name__:
    main()