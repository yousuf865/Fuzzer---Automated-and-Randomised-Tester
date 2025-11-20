import random
from helper import JPEG_mutator
from jpeg_parser import JPEGparser

class JPEGFuzzer:
    def __init__(self):
        self.max_val = 257
        self.min_val = 0
        self.segments = {}
        self.raw_data = b''
        self.parser = JPEGparser()

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
        self.segments, self.raw_data = self.parser.parse(file_path)

    def pattern(self):
        return
    
    # marker, length, data, order, segment
    def mutation_parameters(self, only_double_marker=None, marker_mutate_count=None, mutate_markers=None):
        mutate_count  = 200 if marker_mutate_count is None else marker_mutate_count
        
        # insert "valid" markers randomly
        if only_double_marker:
            return JPEG_mutator.insert_random_markers(self.raw_bytes)

        app0 = self.segments['app0'][0]
        dht = self.segments['dht'][0]
        sos = self.segments['sos'][0]
        
        sof_keys = ['sof0', 'sof1', 'sof2', 'sof3']
        for key in sof_keys:
            if key in self.segments:
                sof = self.segments[key][0]
        
        image_data = sos[4].image_data

        #for marker in jpg_marker_bytes.values():
        #    mutate_bytes = double_markers(self.jpg_bytes, len(self.jpg_bytes), marker)
            
        if random.choice([False, True]):
            self.segments['app0'] = JPEG_mutator.app0_mutation(app0)

        if random.choice([False, True]):
            self.segments['dht'] = JPEG_mutator.huffman_mutate(dht) # the i havent put together the parse here, its in jpeg_parser.py tho

        if random.choice([False, True]):
            self.segments['sos'] = JPEG_mutator.sos_mutate(sos, random.choice([False, True])) # again, still in jpeg_parser.py
        
        if random.choice([False, True]):
            self.segments['sof'] = JPEG_mutator.sof_mutate(sof) # same

        if random.choice([False, True]):
            self.segments['sos'][4].image_data = JPEG_mutator.sos_imagedata_mutation(image_data)
 
        return self.parser.jpeg_constructor(self.markers)
        
            
