import csv
import random
import string

max_val = 257

class Patterns:
    # TODO: Add a way to make more adjustable patterns (so like a checkbox for each type of mutation)
    # Mutations: Numrows, Numcols, Type of values in cells, length of values in cells, etc.

    def flip_file(self, file_path: str) -> None:
        with open(file_path, 'rb') as file:
            content = file.read()

        flipped_content = bytearray(content)
        for i in range(len(flipped_content)):
            flipped_content[i] = flipped_content[i] ^ 0xFF

        with open(file_path, 'wb') as file:
            file.write(flipped_content)
    def json1(self):
        pass
