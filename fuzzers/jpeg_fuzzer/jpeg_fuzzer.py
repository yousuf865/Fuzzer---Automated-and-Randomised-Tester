import random
from helper import JPEG_mutator
from jpeg_parser import JPEGparser

def huffman_mutate(original_huffman=None):
    return

def double_markers(jpg_bytes, jpg_length, mutate_count_for_each_marker=None):
    mutate_count  = 200 if mutate_count_for_each_marker is None else mutate_count_for_each_marker

    for marker in jpg_marker_bytes.values():
        r = random.randint(0, jpg_length)
class JPEGFuzzer:
    def __init__(self):
        self.max_val = 257
        self.min_val = 0
        self.segments = {}

    def get_max_val(self):
        return self.max_val

    def set_max_val(self, max_val: int):
        self.max_val = max_val

    def get_min_val(self):
        return self.min_val

    def set_min_val(self, min_val: int):
        self.min_val = min_val

    # still undefined
    def take_input(self, file_path: str) -> bytes:
        self.segments = JPEGparser.parse(file_path)

    def pattern(self):
        return
    
    def mutation_parameters(self, marker_mutate_count=None, mutate_markers=None):
        mutate_count  = 200 if marker_mutate_count is None else marker_mutate_count



        for marker in jpg_marker_bytes.values():
            mutate_bytes = double_markers(self.jpg_bytes, len(self.jpg_bytes), marker)
            
        if random.choice([False, True]):
            dht = JPEG_mutator.huffman_mutate(dht) # the i havent put together the parse here, its in jpeg_parser.py tho

        if random.choice([False, True]):
            sos = JPEG_mutator.sos_mutate(sos, random.choice([False, True])) # again, still in jpeg_parser.py
        
        if random.choice([False, True]):
            sof = JPEG_mutator.sof_mutate(sof) # same

        if random.choice([False, True]):
            image_data = JPEG_mutator.sos_imagedata_mutation(image_data)

        #TODO return the reconstructed jpeg with JPEG_CONSTRUCTOR in JPEG_PARSER

        pass

            
