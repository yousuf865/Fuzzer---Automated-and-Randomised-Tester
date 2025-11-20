from jpeg_fuzzer import JPEGFuzzer
import subprocess
import sys

fuzzer = JPEGFuzzer()

fuzzer.take_input('../oskar-smethurst-B1GtwanCbiw-unsplash.jpg')

mutated = fuzzer.mutation_parameters()

sys.stdout.buffer.write(mutated)
