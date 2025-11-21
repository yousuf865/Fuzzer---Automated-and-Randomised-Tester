from jpeg_fuzzer import JPEGFuzzer
import subprocess
import sys

fuzzer = JPEGFuzzer()

fuzzer.take_input('../../example_inputs/jpg1.txt')

mutated = fuzzer.mutation_parameters(True)

with open('test.jpg', 'wb') as pic:
    pic.write(mutated)

