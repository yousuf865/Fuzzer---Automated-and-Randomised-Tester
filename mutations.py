import random
import re

class Mutations:
    def __init__(self):
        return

    def bit_flip(self, data_bytes, num_flips):
        for _ in range(num_flips):
            # Find a random byte in byte array
            byte_index = random.randint(0, len(data_bytes) - 1)

            # Pick a random bit in chosen byte to flip
            bit_index = random.randint(0, 7)

            # Turn chosen byte from int to a binary string
            byte_binary = bin(data_bytes[byte_index]).replace('0b', '')

            # Pad binary string to 8 bits
            byte_binary = '0' * (8 - len(byte_binary)) + byte_binary

            # Manually flip the bit in byte
            new_byte_array = [ i for i in byte_binary ]
            if new_byte_array[bit_index] == '1':
                new_byte_array[bit_index] = '0'
            else:
                new_byte_array[bit_index] = '1'
            data_bytes[byte_index] = int(''.join(new_byte_array), 2)

        return data_bytes
    

    def byte_flip(self, data_bytes, num_flips):
        for _ in range(num_flips):
            # Find a random byte in byte array
            byte_index = random.randint(0, len(data_bytes) - 1)

            # Flip chosen byte to new random byte value
            data_bytes[byte_index] = random.randint(0, 255)

        return data_bytes

    def arithmetic_mutation(self, file_path):
        # List of integers to use for arithmetic mutation
        integers = [-1, 0, 1, 2, -2, 100, 65535, 32767, -32768]

        # List of arithmetic operations using integers
        # For division, use floor operator to avoid float values, and also avoid dividing by 0
        operations = [lambda x, y: x +y,
                    lambda x, y: x - y,
                    lambda x, y: x * y,
                    lambda x, y: x // y if y != 0 else x]
               
        f = open(file_path, 'r')
        lines = f.readlines()

        # For each line, find all integers (including negative numbers) and append to list of integers to track for arithmetic mutation
        input_integers = []
        for line in lines:
            input_integers.extend([integer for integer in re.findall(r"[-]?\d+", line)])

        # Randomly choose integers to mutate with arithmetic mutation up to a random number of mutations
        input_integers = random.sample(input_integers, random.randint(0, len(input_integers)))
 
        # Find chosen integers in input, and use a random operation function to apply arithmetic mutation
        mutated_payload = ''
        for line in lines:            
            for number in input_integers:
                # Apply random operation with integer and replace it with the result
                if number in re.findall(r'[-]?\d+', line): 
                    new_integer = random.choice(operations)(int(number), random.choice(integers))
                    line = line.replace(number, str(new_integer))
            mutated_payload += line

        return mutated_payload

    def repeated_parts(self):
        return

    def known_ints(self, file_path):
        known_integers = [0, 1,-1, 65535, 32767, -32768, 2147483647, -2147483648, 4294967295]
        
        f = open(file_path, 'r')
        lines = f.readlines()

        # For each line, find all integers (including negative numbers) and append to list of integers to track for replacement
        input_integers = []
        for line in lines:
            input_integers.extend([integer for integer in re.findall(r"[-]?\d+", line)])

        # Randomly choose integers to replace with known ints up to a random number of replacements
        input_integers = random.sample(input_integers, random.randint(0, len(input_integers)))
 
        # Find chosen integers in input and replace with known ints
        mutated_payload = ''
        for line in lines:            
            for number in input_integers:
                # Make sure it replaces the exact matching integer and not from within another
                if number in re.findall(r'[-]?\d+', line): 
                    line = line.replace(number, str(random.choice(known_integers)))
            mutated_payload += line

        return mutated_payload

    # Run each general mutation strategy
    def run_mutation_strategies(self, input_file, input_type, strategy):

        if strategy == 'bit_flip':
            f = open(input_file, "rb").read()
            mutated_data = self.bit_flip(bytearray(f), 3)
            mutated_payload = mutated_data.decode('utf-8', errors='ignore')
       
        if strategy == 'byte_flip':
            f = open(input_file, "rb").read()
            mutated_data = self.byte_flip(bytearray(f), 3)
            mutated_payload = mutated_data.decode('utf-8', errors='ignore')

        if strategy == 'known_ints':
            mutated_payload = self.known_ints(input_file)

        
        mutated_payload = self.arithmetic_mutation(input_file)

        # print(strategy + '------------' + mutated_payload)

        return mutated_payload
