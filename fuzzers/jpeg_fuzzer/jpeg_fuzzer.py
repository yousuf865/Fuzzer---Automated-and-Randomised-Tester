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
    def mutation_parameters(self, 
                image_data_bool=None, 
                sof_bool=None,
                sos_bool=None,
                dht_bool=None,
                app0_bool=None,
                only_double_marker=None, 
                marker_mutate_count=None, 
                mutate_markers=None
    ):
        mutate_count  = 200 if marker_mutate_count is None else marker_mutate_count
        
        # insert "valid" markers randomly
        if only_double_marker:
            return JPEG_mutator.insert_random_markers(self.raw_bytes)

        app0 = self.segments['app0'][0]
        dht = self.segments['dht']
        sos = self.segments['sos'][0]
        
        sof_keys = ['sof0', 'sof1', 'sof2', 'sof3']
        sof_version = ''
        for key in sof_keys:
            if key in self.segments:
                sof_version = key
                sof = self.segments[key][0]
        
        image_data = sos[4].image_data
        
        if image_data_bool:
            print('only mutating image data------')
            self.segments['sos'][0][4].image_data = JPEG_mutator.sos_imagedata_mutation(image_data)
            return self.parser.jpeg_constructor(self.segments)
    
        print('mutating values---------')
        #for marker in jpg_marker_bytes.values():
        #    mutate_bytes = double_markers(self.jpg_bytes, len(self.jpg_bytes), marker)
            
        if random.choice([False, True]) and app0_bool:
            print('mutating app0')
            self.segments['app0'][0] = JPEG_mutator.app0_mutation(app0)

        if random.choice([False, True]) and dht_bool:
            print('mutating dht')
            self.segments['dht'] = JPEG_mutator.dht_mutate(dht)

        if random.choice([False, True]) and sos_bool:
            print('mutating sos')
            self.segments['sos'][0] = JPEG_mutator.sos_mutate(sos, random.choice([False, True])) # again, still in jpeg_parser.py
        
        print('check')
        if random.choice([False, True]) and sof_bool:
            print('mutating sof')
            self.segments[sof_version][0] = JPEG_mutator.sof_mutate(sof) # same

        if random.choice([False, True]) and (image_data_bool is None or image_data_bool) :
            print('mutating image data')
            self.segments['sos'][0][4].image_data = JPEG_mutator.sos_imagedata_mutation(image_data)
 
        return self.parser.jpeg_constructor(self.segments)
        
            
