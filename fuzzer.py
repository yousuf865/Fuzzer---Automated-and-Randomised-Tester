import subprocess
import csv
import os
import random
import string
import subprocess
import glob
import shutil
import time
import magic
import inspect
# Custom imports/defined classes
from fuzzers.csv_fuzzer import CSVFuzzer
from fuzzers.json_fuzzer import JSONFuzzer
from fuzzers.xml_fuzzer import XMLFuzzer
from fuzzers.plaintext_fuzzer import PlainTextFuzzer
from fuzzers.xml_fuzzer import XMLFuzzer
from mutations import Mutations
import itertools
csv_fuzzer = CSVFuzzer()
json_fuzzer = JSONFuzzer()
xml_fuzzer = XMLFuzzer()
plaintext_fuzzer = PlainTextFuzzer()
xml_fuzzer = XMLFuzzer()
mutations = Mutations()
file_magic = magic.Magic()


class Fuzzer:
    def __init__(self):
        return
    
    def create_output_dir(self):
        if "fuzzer_output" not in os.listdir():
            os.mkdir("fuzzer_output")

    def reset_output_dir(self):
        self.create_output_dir()
        # Clear all files from the fuzzer_output directory
        file_list = os.listdir("fuzzer_output")
        for file_name in file_list:
            file_path = os.path.join("fuzzer_output", file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    ### WIP!
    # TODO: Possibly make the tests more predefined to make it less taxing
    def run_target(self, src: str, payload: str):
        try:
            start_time = time.time()
            process = subprocess.run(['./' + src], input=payload, capture_output=True, text=True)
            end_time = time.time()
            
            elapsed_time = end_time - start_time
            output = process.stdout
            error = process.stderr
            return_code = process.returncode
            return return_code, output, error, elapsed_time
        except Exception as e:
            return -1, "", f"Error: {e}", 0.0

    def count_positional_args(self, func):
        # Get the signature of the function
        sig = inspect.signature(func)
        
        # Count the number of positional arguments in a function
        positional_args = [
            param for param in sig.parameters.values()
            if param.default == inspect.Parameter.empty and
            param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        return len(positional_args)

    def sample_name(self, bin_name: str, file_type, file_type_dict: dict, num_tests: int = 100):
        crash_map = {}
        max_val_bin = {
            "csv1": 257,
            "csv2": 257
        }
        input_type = "filler"

        for item in file_type_dict.keys():      
            if item in file_type:
                input_type = item
                break
        # check for imp
        if input_type in file_type_dict.keys():
            if bin_name in max_val_bin.keys():
                file_type_dict[input_type].set_max_val(max_val_bin[bin_name])
            self.create_output_dir()
            # checks for the amount of arguments in the function
            arg_amount = self.count_positional_args(file_type_dict[input_type].mutation_parameters)
            # check for default values implementation
            # maybe have this be the only check? 
            try:
                normal_values = file_type_dict[input_type].take_input(f"example_inputs/{bin_name}.txt")
            except Exception as e:
                return f"Error in the implementation: {e}"
            
            # Apply General Mutation Strategies on given example input to create mutated payloads
            strategies = ['bit_flip', 'byte_flip', 'known_ints', 'arithmetic']
            print("RUNNING GENERAL MUTATION STRATEGIES  ", end="\r", flush=True)
            for strat in strategies:
                # break
                for i in range(1, num_tests):
                    mutated_payload = mutations.run_mutation_strategies(f"example_inputs/{bin_name}.txt", input_type, strat)
                    print(mutated_payload)
                    return_code, output, error, elapsed_time = self.run_target(f"binaries/{bin_name}", mutated_payload)
                    
                    is_new_crash = True
                    if "Error:" in output or error != "" or return_code != 0:
                        prev_crashes = crash_map.get(return_code, [])
                        for crash in prev_crashes:
                            if crash[0] == error and crash[1] == output:
                                # take this payload as new crash
                                prev_elapsed = crash[3] if len(crash) > 3 else 0.0
                                if prev_elapsed == 0.0:
                                    diff_ratio = 1.0 if elapsed_time != 0.0 else 0.0
                                else:
                                    diff_ratio = abs(elapsed_time - prev_elapsed) / prev_elapsed

                                if diff_ratio < 0.6:
                                    is_new_crash = False
                                    break
                        # We do this to get the specifics of the error output via GDB
                        summary = f"Test {i} for {bin_name}:\n{error}\nFound with these parameters:\n{strat}\n"
                        with open(f"fuzzer_output/bad_{bin_name}.txt", "a+") as file:
                            file.write(f"{mutated_payload}")
                            return summary                       
                    output_dict = {f'output_{i}': output, f'strategy_{i}': strat}

                    if output not in output_list:
                        output_list.append(output)
                        unique_output_mutations.append(output_dict)
                        hhh[output] = strat


            # Apply Mutation Parameters derived from example input to generate new random payloads
            print("RUNNING MUTATION PARAMETERS BASED ON FILE TYPE   ", end="\r", flush=True)
            args_mutation = [False for _ in range(arg_amount-1)]
            num_args = max(0, arg_amount - 1)
            if num_args == 0:
                all_combinations = [[]]
            else:
                all_combinations = [list(c) for c in itertools.product([False, True], repeat=num_args)]

            # initialize args_mutation to the first combination (loop later can cycle through all_combinations)
            args_mutation = all_combinations[0]
            args_mutation_index = 0
            flip_arg_mutation_at = 0
            avg_elapsed_time = 0.0
            # arg_mutation_summary = {}
            for i in range (1, num_tests):
                # auto populates the args_mutation list with random True/False values
                # could change this to be modifiable depending on the implementation
                # so each implementation can have different inputs
                
                patterns_list = file_type_dict[input_type].mutation_parameters(
                        *args_mutation,
                        normal_values
                )
                payload = patterns_list[0]
                mutation_type = patterns_list[1]
                
                return_code, output, error, elapsed_time = self.run_target(f"binaries/{bin_name}", payload)
                print(f'bin: {bin_name} | test: {i}/{num_tests} | return code: {return_code} | elapsed time: {elapsed_time:.4f}s | args_index: {args_mutation_index}/{len(all_combinations)-1} | stderr: {error}    ')
                if return_code != 0:
                    print(f'Non-zero return code detected: {return_code}, stderr: {error}, output: {output}')
                    return summary
                if elapsed_time != 0.0:
                    if avg_elapsed_time > 0.0:
                        diff_ratio = abs(elapsed_time - avg_elapsed_time) / avg_elapsed_time
                        if diff_ratio <= 0.1 and i - flip_arg_mutation_at >= 10 :
                            args_mutation_index = (args_mutation_index + 1) % len(all_combinations)
                            flip_arg_mutation_at = i
                            args_mutation = all_combinations[args_mutation_index]
                            
                avg_elapsed_time = (avg_elapsed_time * (i - 1) + elapsed_time) / i

                if "Error:" in output or error != "":
                    # We do this to get the specifics of the error output via GDB
                    summary = f"Test {i} for {bin_name}:\n{error}\nFound with these parameters:\n{mutation_type}\n"
                    with open(f"fuzzer_output/bad_{bin_name}.txt", "w+") as file:
                        file.write(f"{payload}")
                    output = error
                    return summary
                
                output_dict = {f'output_{i}': output, f'mutation_type_{i}': mutation_type}

                if output not in output_list:
                    output_list.append(output)
                    unique_output_mutations.append(output_dict)
                    hhh[output] = mutation_type
        
        else:
            print(f"Error: {bin_name} not implemented yet!\nMoving onto the next binary...", end="\r", flush=True)
        return summary


    # So far this is specified for csv1, but we can eventually change this to be more general
    def auto_test(self, bin_name: str, num_tests: int = 100) -> None:
        # This is the input read in
        file_type = file_magic.from_file(f"example_inputs/{bin_name}.txt")
        if "HTML" in file_type:
          file_type = "XML"
        if 'csv2' in bin_name:
            file_type = "CSV"
        else: 
            return
        file_type_dict = {
            "CSV": csv_fuzzer,
            "JSON": json_fuzzer,
            "ASCII": plaintext_fuzzer,
            "XML": xml_fuzzer,
            "data": plaintext_fuzzer   
        }
        return self.sample_name(bin_name, file_type, file_type_dict, num_tests)

    def manual_test(self,
        bin_name: str,
        bin_params: dict
        ) -> None:
        '''
        USAGE: 
            bin_name: str - the name of the binary to test
            bin_params: dict - a dictionary containing the parameters for the mutation
        GENERAL DESCRIPTION:
            This function generates a payload based on the parameters provided in bin_params 
            and then runs the target binary with the generated payload. 
            The output is then written to a file.
        '''
        payload = ""
        if "csv" in bin_name:
            payload = csv_fuzzer.pattern(
                bin_params["header"],
                bin_params["num_rows"],
                bin_params["num_cols"],
                bin_params["value_type"],
                bin_params["cell_val_len"]
            )
            mutation_type =(
                bin_params["header"],
                bin_params["num_rows"],
                bin_params["num_cols"],
                bin_params["value_type"],
                bin_params["cell_val_len"]
            )
        
        if payload != "":
            output, error = self.run_target(f"binaries/{bin_name}", payload)
            with open(f"fuzzer_output/manual_input_{bin_name}.txt", "w") as file:
                file.write(f"Mutation type: {mutation_type}\n")
                # file.write(f"Payload: {payload}\n")
                file.write(f"Output: {output}\n")
            print(f"Manual test written to manual_input_{bin_name}.txt")
            with open(f"fuzzer_output/manual_input_payload_{bin_name}.txt", "w") as file:
                file.write(payload)
        else:
            print("Error: No payload generated")

    def standard_test(self, bin_name: str, num_tests: int = 100) -> None:
        # Use this to test automatic and manual inputs
        self.auto_test(bin_name, num_tests)
        # Example usage of manual_test:
        test_dict = {
            "header": ['header', 'must', 'stay', 'intact'],
            "num_rows": 15,
            "num_cols": 4,
            "value_type": 'hex',
            "cell_val_len": 296
        }
        self.manual_test(bin_name, test_dict)

    def length_rnd(self):
        return
    
    def val_rnd(self):
        return
    
    def pattern_rnd(self, pattern: str):
        return
