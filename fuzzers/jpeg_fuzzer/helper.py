import random
import copy
from mutations import Mutations # i dont know how to import

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


#table_data {
#    'table_type': table_id, 
#    'code_lengths': code_lengths,
#    'table': code_table
#}
# original_huffman = array of table_data
def huffman_mutate(original_dht, mutate_table_id=None, mutate_code_amounts=None):
    dht = copy.deepcopy(original_dht)

    # --------------------------------- Mutate table ------------------------------
    # randomise tables to mutate
    tables_to_mutate = []
    r = random.randint(0, len(dht))
    for i in range(r):
        tables_to_mutate.append(dht[random.randint(0, len(dht))])

    # mutate table
    for table_data in tables_to_mutate:
        table = table_data['table']
        strategies = [Mutations().bit_flip()]
        strat = random.choice(strategies)

        table = Mutations().bit_flip(table, random.randint(0, len(table)))
        table_data['table_id'] = random.randint(0,32)

        table_bit_idx = 0
        for i in range(0, 16):
            random_boolean = random.choice([True, False])
             
            table_bit_idx += table_data['code_lengths'][i] 
            
            # the amount of code of length i to be added, right now only up to 5 additions
            add_code_num = random.randint(0, 5) if random_boolean else 0
            
            # randomise minus or not (addition can be minus as well right :P)
            # forgive bad variable name
            add_code_num *= -1 if random.choice([True, False]) else 1
            
            if add_code_num >= 0:
                addition_bits = [random.choice([0, 1]) for _ in range(add_code_num)]
                
                table = table[:table_bit_idx] + addition_bits + table[table_bit_idx:]
                
                # adjust index after addition to still be on current index
                table_bit_idx += add_code_num
                table_data['code_lengths'][i] += add_code_num
            else:
                table_bit_idx -= add_code_num

                table = table[:table_bit_idx] + table[table_bit_idx:]
                table_data['code_lengths'][i] -= add_code_num

    return dht



# random position of a marker (possibly making it double)
def double_markers(jpg_bytes, jpg_length, marker):
    mutate_count  = 200 if marker_mutate_count is None else marker_mutate_count

    r = random.randint(0, jpg_length)

    return jpg_bytes[:r] + marker + jpg_bytes[(r + 2):]
