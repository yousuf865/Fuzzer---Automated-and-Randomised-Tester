import random
import helper.py

jpg_markers_bytes = {
    # Start/End Markers
    "Start of Image (SOI)": b'\xff\xd8',
    "End of Image (EOI)": b'\xff\xd9',
    "Start of Scan (SOS)": b'\xff\xda',

    # Frame/Define Markers
    "Start of Frame (SOF0 - Baseline DCT)": b'\xff\xc0',
    "Start of Frame (SOF1 - Extended sequential DCT)": b'\xff\xc1',
    "Start of Frame (SOF2 - Progressive DCT)": b'\xff\xc2',
    "Start of Frame (SOF3 - Lossless sequential)": b'\xff\xc3',
    "Define Huffman Table (DHT)": b'\xff\xc4',
    "Define Arithmetic Coding Conditioning (DAC)": b'\xff\xcc',
    "Define Quantization Table (DQT)": b'\xff\xdb',

    # Restart Markers (RST0-RST7)
    "Restart Marker 0 (RST0)": b'\xff\xd0',
    # ... RST1 through RST6 markers would be FFD1 through FFD6 ...
    "Restart Marker 7 (RST7)": b'\xff\xd7',

    # Application Markers
    "Application Specific (APP0 - JFIF/JPEGE)": b'\xff\xe0',
    "Application Specific (APP1 - Exif/XMP)": b'\xff\xe1',
    "Application Specific (APP2 - ICC/FlashPix)": b'\xff\xe2'
    "Application Specific (APP13 - Photoshop IRB/8BIM)": b'\xff\xed',

    # Other Markers
    "Comment (COM)": b'\xff\xfe',
    "Define Restart Interval (DRI)": b'\xff\xdd',
}

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
        self.jpg_bytes = None

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
        with open(file_path, 'rb') as file:
            self.jpg_bytes = file.read()

    def pattern(self):
        return
    
    def mutation_parameters(self, marker_mutate_count=None):
        if self.jpg_bytes == None:
            print('jpg not recieved!')
            return 

        mutate_count  = 200 if marker_mutate_count is None else marker_mutate_count

        for marker in jpg_marker_bytes.values():
            mutate_bytes = double_markers(self.jpg_bytes, len(self.jpg_bytes), marker)
            
        
    


            
