from jpeg_fuzzer import JPEGFuzzer
import subprocess
import sys

fuzzer = JPEGFuzzer()

fuzzer.take_input('../../example_inputs/jpg1.txt')

mutated = fuzzer.mutation_parameters(None, True, True, True, True, True)

with open('test.jpg', 'wb') as pic:
    pic.write(mutated)

result = subprocess.run(['open', 'test.jpg'], capture_output=True, text=True)
print("Stdout:", result.stdout)
print("Stderr:", result.stderr)
print("Exit Code:", result.returncode)
