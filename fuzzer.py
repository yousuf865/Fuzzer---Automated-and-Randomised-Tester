import subprocess
import resource
import os
import subprocess
import shutil
import time
import magic
import inspect
import itertools
# Custom imports/defined classes
from fuzzers.csv_fuzzer import CSVFuzzer
from fuzzers.json_fuzzer import JSONFuzzer
from fuzzers.xml_fuzzer import XMLFuzzer
from fuzzers.plaintext_fuzzer import PlainTextFuzzer
from fuzzers.xml_fuzzer import XMLFuzzer
from mutations import Mutations
from collections import Counter


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
                
    def check_for_csv(self, bin_name: str) -> bool:
        # Try to read the example input and refine detection for ASCII files
        try:
            with open(f"example_inputs/{bin_name}.txt", "r", errors="ignore") as _f:
                sample = _f.read()
                lines = sample.splitlines()
                lines = [ln for ln in lines if ln.strip()]
                if lines:
                    comma_counts = [ln.count(',') for ln in lines]
                    # all lines have same non-zero number of commas -> treat as CSV
                    if len(set(comma_counts)) == 1 and comma_counts[0] > 0:
                        return True
                    else:
                        # fallback: if a strong majority of lines share the same non-zero comma count, treat as CSV
                        cnt = Counter(comma_counts)
                        most_common_count, freq = cnt.most_common(1)[0]
                        if most_common_count > 0 and freq >= max(1, int(0.8 * len(comma_counts))):
                            return True
                        else:
                            return False
                else:
                    return False
        except Exception:
            sample = ""
        return False
    ### WIP!
    # TODO: Possibly make the tests more predefined to make it less taxing
    def run_target(self, src: str, payload: str):
        try:
            start_time = time.time()
            before = resource.getrusage(resource.RUSAGE_CHILDREN)
            process = subprocess.run(['./' + src], input=payload, capture_output=True, text=True, timeout=0.5)
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            cpu_time = (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
            end_time = time.time()
            
            elapsed_time = end_time - start_time
            output = process.stdout
            error = process.stderr
            return_code = process.returncode

            return return_code, output, error, elapsed_time, cpu_time
        except subprocess.TimeoutExpired:
            end_time = time.time()
            elapsed_time = end_time - start_time
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            cpu_time = (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
            # print(f"Elapsed time: {elapsed_time}, CPU time: {cpu_time}")
            return 0, "", "Error: TimeoutExpired", elapsed_time, cpu_time
        except Exception as e:
            # print(f"Error running target: {e}") 
            return 0, "", f"Error: {e}", 0.0, 0.0

    def count_positional_args(self, func):
        sig = inspect.signature(func)
        positional_args = [
            param for param in sig.parameters.values()
            if param.default == inspect.Parameter.empty and
            param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        return len(positional_args)

    def is_this_a_sleeper_or_looper(self, cpu_time, elapsed_time) -> int:
        if elapsed_time <= 0.5:
            return 0
        cpu_fraction = cpu_time / elapsed_time
        if cpu_fraction < 0.5:
            return 1
        if elapsed_time > 0.5:
            return 2
        return 0

    def should_start_loop_check(self, elapsed_time: float) -> bool:  
        return elapsed_time > 2.0
    def is_this_a_crash(self, return_code: int, stderr: str) -> bool:
        if return_code < 0 and return_code != -6:
            return True
        if return_code == -6 and 'stack smash' in stderr.lower():
            return True
        return False
    
    def do_fuzzin(self, bin_name: str, file_type, file_type_dict: dict, num_tests: int = 100):
        start_time = time.time()
        sleep_count = 0
        loop_count = 0
        max_hits = 10
        watch_for_loops = False
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
            arg_amount = self.count_positional_args(file_type_dict[input_type].mutation_parameters)
            try:
                normal_values = file_type_dict[input_type].take_input(f"example_inputs/{bin_name}.txt")
            except Exception as e:
                return f"Error in the implementation: {e}"
            strategies = ['bit_flip', 'byte_flip', 'known_ints', 'arithmetic']
            print("RUNNING GENERAL MUTATION STRATEGIES  ", end="\r", flush=True)
            strat_index = 0

            for i in range(num_tests):
                if time.time() - start_time >= 54:
                    return {0: [("No errors found, Time limit reached, hangs detected: sleeps={}, loops={}".format(sleep_count, loop_count), "",
                                time.time() - start_time, "time_limit")]}

                strat = strategies[strat_index]

                mutated_payload = mutations.run_mutation_strategies(
                    f"example_inputs/{bin_name}.txt", input_type, strat
                )
                return_code, output, error, elapsed_time, cpu_time = \
                    self.run_target(f"binaries/{bin_name}", mutated_payload)
                    
                sleeper_or_looper = self.is_this_a_sleeper_or_looper(cpu_time, elapsed_time)
                if sleeper_or_looper == 1:
                    sleep_count += 1
                    strat_index = (strat_index + 1) % len(strategies)
                elif sleeper_or_looper == 2:
                    loop_count += 1
                    strat_index = (strat_index + 1) % len(strategies)
                if sleep_count + loop_count >= max_hits:
                    break
                
                strat_index = (i // (num_tests // len(strategies))) % len(strategies)


                if self.is_this_a_crash(return_code, error):
                    with open(f"fuzzer_output/bad_{bin_name}.txt", "a+") as file:
                        file.write(f"{mutated_payload}")
                    return {
                        return_code: [(error, output, elapsed_time, strat)]
                    }



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
                # print(f"Test {i}/{num_tests} | ar_index: {args_mutation_index}")
                if time.time() - start_time >= 54:
                    return {0: [("No errors found, Time limit reached, hangs detected: sleeps={}, loops={}".format(sleep_count, loop_count), "", time.time() - start_time, "time_limit")]}
                patterns_list = file_type_dict[input_type].mutation_parameters(
                        *args_mutation,
                        normal_values
                )
                payload = patterns_list[0]
                return_code, output, error, elapsed_time, cpu_time = self.run_target(f"binaries/{bin_name}", payload)
                if watch_for_loops == False and self.should_start_loop_check(elapsed_time):
                        watch_for_loops = True
                if elapsed_time != 0.0:
                    if avg_elapsed_time > 0.0:
                        diff_ratio = abs(elapsed_time - avg_elapsed_time) / avg_elapsed_time
                        if diff_ratio <= 0.1 and i - flip_arg_mutation_at >= 10 or self.is_this_a_sleeper_or_looper(cpu_time, elapsed_time) > 0:
                            args_mutation_index = (args_mutation_index + 1) % len(all_combinations)
                            flip_arg_mutation_at = i
                            args_mutation = all_combinations[args_mutation_index]
                            
                avg_elapsed_time = (avg_elapsed_time * (i - 1) + elapsed_time) / i
                
                sleeper_or_looper = self.is_this_a_sleeper_or_looper(cpu_time, elapsed_time)
                if sleeper_or_looper == 1:
                    sleep_count += 1
                    strat_index = (strat_index + 1) % len(strategies)
                elif sleeper_or_looper == 2:
                    loop_count += 1
                    strat_index = (strat_index + 1) % len(strategies)
                if sleep_count + loop_count >= max_hits*2:
                    break

                if self.is_this_a_crash(return_code, error):
                    with open(f"fuzzer_output/bad_{bin_name}.txt", "a+") as file:
                        file.write(f"{payload}")
                    return {return_code:[ (error, output, elapsed_time, 'param_mutation')]}
        return {0: [("No errors found, Exhausted max tests, hangs detected: sleeps={}, loops={}".format(sleep_count, loop_count), "", time.time() - start_time, "no_crash")]}


    # So far this is specified for csv1, but we can eventually change this to be more general
    def auto_test(self, bin_name: str, num_tests: int = 100) -> None:
        # This is the input read in
        file_type = file_magic.from_file(f"example_inputs/{bin_name}.txt")
        if "HTML" in file_type:
          file_type = "XML"
        if "ASCII" in file_type and "CSV" not in file_type:
            if self.check_for_csv(bin_name):
                file_type = "CSV"

        file_type_dict = {
            "CSV": csv_fuzzer,
            "JSON": json_fuzzer,
            "ASCII": plaintext_fuzzer,
            "XML": xml_fuzzer,
            "data": plaintext_fuzzer   
        }
        return self.do_fuzzin(bin_name, file_type, file_type_dict, num_tests)
