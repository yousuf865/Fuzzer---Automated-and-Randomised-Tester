from jpeg_fuzzer import JPEGFuzzer
import subprocess
import sys

fuzzer = JPEGFuzzer()

fuzzer.take_input('example_inputs/jpg1.txt')

mutated = fuzzer.mutation_parameters(True)

try:
    sys.stdout.buffer.write(mutated)
    sys.stdout.buffer.flush()

except BrokenPipeError:
    # Handle the error and exit gracefully
    try:
        sys.stdout.close()
    except:
        pass
    sys.exit(0)

